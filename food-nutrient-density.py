# -*- coding: utf-8 -*-
"""
USDA FoodData Central: Data Processing, ETL & Statistical Analysis Pipeline

This script performs ETL (Extract, Transform, Load) operations and statistical analysis
on the USDA FoodData Central SR Legacy JSON dataset.

Key Operations:
1. JSON Parsing & Feature Extraction: Normalizes raw JSON into a tabular structure.
2. Data Cleaning & Filtering: Removes irrelevant food categories and non-food items.
3. Categorization & Rule-Based Tagging: Groups products into 10 macro categories and
   classifies processing types (Raw vs. Cooked/Processed).
4. Feature Engineering: Calculates caloric splits, Nutrient Density Index (NDI), and dietary flags.
5. Statistical Testing: Conducts IQR outlier analysis, Spearman correlations,
   Mann-Whitney U tests (with FDR correction), and Kruskal-Wallis variance tests.
6. Data Reshaping: Exports clean datasets in both wide and long formats for Tableau / Power BI.
"""

import json
import re
from collections import Counter

import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests


# ==============================================================================
# STEP 1: DATA EXTRACTION & JSON PARSING
# ==============================================================================

# Path to raw JSON data file
file_path = '/FoodData_Central_sr_legacy_food_json_2018-04.json'

with open(file_path, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

foods_list = raw_data.get('SRLegacyFoods', raw_data)

parsed_foods = []

for food in foods_list:
    row = {
        'fdc_id': food.get('fdcId'),
        'description': food.get('description'),
        'category': food.get('foodCategory', {}).get('description')
    }

    for item in food.get('foodNutrients', []):
        nutrient_info = item.get('nutrient') or {}
        name = (nutrient_info.get('name') or '').strip()
        unit = (nutrient_info.get('unitName') or '').strip().lower()
        amount = item.get('amount')

        if amount is None:
            continue

        # Energy & Energy Sub-components
        if name == 'Energy' and unit == 'kcal':
            row['calories_kcal'] = amount
        elif name == 'Protein':
            row['protein_g'] = amount
        elif name == 'Total lipid (fat)':
            row['fat_g'] = amount
        elif name == 'Carbohydrate, by difference':
            row['carbs_g'] = amount
        elif name == 'Fiber, total dietary':
            row['fiber_g'] = amount
        elif name == 'Total Sugars':
            row['sugars_g'] = amount
        elif name == 'Fatty acids, total saturated':
            row['saturated_fat_g'] = amount
        elif name == 'Fatty acids, total trans':
            row['trans_fat_g'] = amount
        elif name == 'Cholesterol':
            row['cholesterol_mg'] = amount
        elif name == 'Water':
            row['water_g'] = amount
        elif name == 'Ash':
            row['ash_g'] = amount

        # Essential Minerals
        elif name == 'Sodium, Na':
            row['sodium_mg'] = amount
        elif name == 'Potassium, K':
            row['potassium_mg'] = amount
        elif name == 'Calcium, Ca':
            row['calcium_mg'] = amount
        elif name == 'Iron, Fe':
            row['iron_mg'] = amount
        elif name == 'Magnesium, Mg':
            row['magnesium_mg'] = amount
        elif name == 'Phosphorus, P':
            row['phosphorus_mg'] = amount
        elif name == 'Zinc, Zn':
            row['zinc_mg'] = amount

        # Essential Vitamins & Compounds
        elif name == 'Vitamin C, total ascorbic acid':
            row['vitamin_c_mg'] = amount
        elif 'Vitamin A' in name:
            if 'RAE' in name or unit in ['µg', 'ug', 'mcg']:
                row['vitamin_a_mcg'] = amount
            elif unit == 'iu' and 'vitamin_a_mcg' not in row:
                row['vitamin_a_mcg'] = round(amount / 3.33, 1)
        elif 'Vitamin D' in name:
            if unit in ['µg', 'ug', 'mcg']:
                row['vitamin_d_mcg'] = amount
            elif unit == 'iu' and 'vitamin_d_mcg' not in row:
                row['vitamin_d_mcg'] = round(amount / 40, 2)
        elif 'Vitamin B-12' in name:
            row['vitamin_b12_mcg'] = amount
        elif name == 'Vitamin E (alpha-tocopherol)':
            row['vitamin_e_mg'] = amount
        elif name == 'Vitamin B-6':
            row['vitamin_b6_mg'] = amount
        elif name == 'Caffeine':
            row['caffeine_mg'] = amount

    parsed_foods.append(row)

# Create raw structured DataFrame
df_raw = pd.DataFrame(parsed_foods)


# ==============================================================================
# STEP 2: DATA CLEANING & CATEGORY FILTERING
# ==============================================================================

# 1. Remove non-representative background food categories
noise_categories = [
    'Baby Foods',
    'American Indian/Alaska Native Foods',
    'Restaurant Foods',
    'Meals, Entrees, and Side Dishes'
]
df_filtered = df_raw[~df_raw['category'].isin(noise_categories)].copy()

# 2. Filter out highly fortified/infant-specific items via keywords
keywords_to_remove = 'baby|infant|formula|fortified'
df_filtered = df_filtered[
    ~df_filtered['description'].str.contains(keywords_to_remove, case=False, na=False)
].copy()


# ==============================================================================
# STEP 3: CATEGORIZATION & PROCESSING STATUS CLASSIFICATION
# ==============================================================================

# Regex rule-sets for thermal state determination
raw_pattern = r'\b(?:raw|fresh|unprocessed|uncooked|unheated|unprepared|unbaked)\b'
cooked_pattern = (
    r'\b(?:cooked|boiled|roasted|baked|fried|steamed|grilled|toasted|'
    r'broiled|microwaved|ready[- ]?to[- ]?(?:eat|heat|serve)|prepared|'
    r'commercially prepared|prepared[- ]from[- ]recipe|canned|pasteurized|pickled|preserved)\b'
)
ready_product_pattern = (
    r'\b(?:bread|bagels?|rolls?|buns?|muffins?|cookies?|crackers?|cakes?|pastr(?:y|ies)|'
    r'waffles?|pancakes?|doughnuts?|pretzels?|tostadas?|tortillas?|focaccia|chips?|'
    r'granola bars?|fruit leather|beef jerky|popcorn|rice cakes?|trail mix|cand(?:y|ies)|'
    r'chocolate|fudge|marshmallows?|caramels?|jellybeans?|gumdrops?|ice cream|sherbet|'
    r'frozen yogurt|pudding|puddings?|flan|eclair|cream puff|pizza|pie|pies|sandwich|'
    r'sandwiches|smoothie|smoothies|juice|nectar)\b'
)
not_ready_pattern = (
    r'\b(?:dough|batter|raw|uncooked|unprepared|unbaked|unheated|'
    r'ready[- ]?to[- ]?(?:bake|fry|cook)|refrigerated dough|dry mix|'
    r'dry powdered mix|dry powder)\b'
)
frozen_raw_pattern = r'(?=.*\bfrozen\b)(?=.*\b(?:raw|uncooked|unprepared|unbaked|unheated)\b)'
frozen_cooked_pattern = r'(?=.*\bfrozen\b)(?=.*\b(?:cooked|ready[- ]?to[- ]?(?:eat|heat|serve)|microwaved|toasted)\b)'

# Apply conditions in priority order
conditions_processing = [
    df_filtered['description'].str.contains(frozen_raw_pattern, case=False, na=False, regex=True),
    df_filtered['description'].str.contains(not_ready_pattern, case=False, na=False, regex=True),
    df_filtered['description'].str.contains(raw_pattern, case=False, na=False, regex=True) & 
    ~df_filtered['description'].str.contains(cooked_pattern, case=False, na=False, regex=True),
    df_filtered['description'].str.contains(frozen_cooked_pattern, case=False, na=False, regex=True),
    df_filtered['description'].str.contains(cooked_pattern, case=False, na=False, regex=True),
    df_filtered['description'].str.contains(ready_product_pattern, case=False, na=False, regex=True) & 
    ~df_filtered['description'].str.contains(not_ready_pattern, case=False, na=False, regex=True)
]

choices_processing = [
    'Raw / Whole Food',
    'Raw / Whole Food',
    'Raw / Whole Food',
    'Cooked / Processed',
    'Cooked / Processed',
    'Cooked / Processed'
]

df_filtered['processing_type'] = np.select(conditions_processing, choices_processing, default='Unknown')

# Map categories into 10 cohesive business Macro Groups
def assign_macro_group(cat):
    if pd.isna(cat):
        return 'Other'
    
    cat_lower = str(cat).lower()
    if 'vegetable' in cat_lower or 'legume' in cat_lower:
        return 'Vegetables & Legumes'
    elif 'fruit' in cat_lower:
        return 'Fruits'
    elif 'nut' in cat_lower or 'seed' in cat_lower:
        return 'Nuts & Seeds'
    elif 'finfish' in cat_lower or 'shellfish' in cat_lower:
        return 'Seafood & Fish'
    elif any(x in cat_lower for x in ['beef', 'pork', 'poultry', 'lamb', 'sausages', 'veal', 'game', 'meat']):
        return 'Meat & Poultry'
    elif any(x in cat_lower for x in ['dairy', 'egg']):
        return 'Dairy & Eggs'
    elif any(x in cat_lower for x in ['cereal', 'baked', 'grain']):
        return 'Grains & Bakery'
    elif any(x in cat_lower for x in ['snack', 'sweets', 'beverages', 'fast foods']):
        return 'Snacks, Sweets & Fast Food'
    elif 'fats' in cat_lower or 'oils' in cat_lower:
        return 'Fats & Oils'
    elif any(x in cat_lower for x in ['soups', 'sauces', 'spices']):
        return 'Soups, Sauces & Spices'
    else:
        return 'Other'

df_filtered['macro_group'] = df_filtered['category'].apply(assign_macro_group)


# ==============================================================================
# STEP 4: FEATURE ENGINEERING & METRIC CALCULATION
# ==============================================================================

df_engineered = df_filtered.copy()

# Zero-safe vector for energy calculations
calories_safe = df_engineered['calories_kcal'].replace(0, np.nan)

# 1. Macro-Nutrient Caloric Breakdown (%)
df_engineered['protein_cal_pct'] = ((df_engineered['protein_g'] * 4) / calories_safe * 100).fillna(0).clip(0, 100).round(1)
df_engineered['fat_cal_pct'] = ((df_engineered['fat_g'] * 9) / calories_safe * 100).fillna(0).clip(0, 100).round(1)
df_engineered['carb_cal_pct'] = ((df_engineered['carbs_g'] * 4) / calories_safe * 100).fillna(0).clip(0, 100).round(1)

# 2. Dietary & Nutrition Binary Flags
df_engineered['is_high_protein'] = (df_engineered['protein_cal_pct'] >= 25) | (df_engineered['protein_g'] >= 15)
df_engineered['is_keto_friendly'] = (df_engineered['carb_cal_pct'] <= 10) & (df_engineered['fat_cal_pct'] >= 65)
df_engineered['is_low_calorie'] = df_engineered['calories_kcal'] <= 100
df_engineered['is_high_fiber'] = df_engineered['fiber_g'] >= 5


# ==============================================================================
# STEP 5: STATISTICAL ANALYSIS & HYPOTHESIS TESTING
# ==============================================================================

# Target nutrient columns for analytics
nutrient_cols = [
    'protein_g', 'fat_g', 'carbs_g', 'calories_kcal', 'water_g', 'sugars_g', 'fiber_g',
    'calcium_mg', 'iron_mg', 'magnesium_mg', 'phosphorus_mg', 'potassium_mg', 'sodium_mg', 'zinc_mg',
    'vitamin_a_mcg', 'vitamin_c_mg', 'vitamin_b6_mg', 'vitamin_b12_mcg', 'vitamin_d_mcg', 'vitamin_e_mg',
    'cholesterol_mg', 'saturated_fat_g', 'trans_fat_g', 'caffeine_mg', 'ash_g'
]

# 1. Outlier Inspection via Interquartile Range (IQR)
def detect_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] < lower_bound) | (df[column] > upper_bound)]

outliers_summary = {col: len(detect_outliers_iqr(df_engineered, col)) for col in nutrient_cols if col in df_engineered.columns}

# 2. Category Variance Significance (Kruskal-Wallis Test)
category_samples = [group['calories_kcal'].dropna() for name, group in df_engineered.groupby('macro_group')]
kw_stat, kw_p = stats.kruskal(*category_samples)

# 3. Thermal State Nutrient Differences (Mann-Whitney U Test + Benjamini-Hochberg FDR Correction)
macro_groups = df_engineered['macro_group'].dropna().unique()
statistical_results = []

for group in macro_groups:
    group_df = df_engineered[df_engineered['macro_group'] == group]
    raw_df = group_df[group_df['processing_type'] == 'Raw / Whole Food']
    cooked_df = group_df[group_df['processing_type'] == 'Cooked / Processed']

    for nutrient in nutrient_cols:
        raw = raw_df[nutrient].dropna()
        cooked = cooked_df[nutrient].dropna()

        if len(raw) < 5 or len(cooked) < 5:
            continue

        u_stat, p_val = stats.mannwhitneyu(raw, cooked, alternative='two-sided')
        
        raw_med = raw.median()
        cooked_med = cooked.median()
        med_diff = cooked_med - raw_med
        
        # Rank-Biserial Correlation Effect Size calculation
        n_raw, n_cooked = len(raw), len(cooked)
        rank_biserial = ((2 * u_stat) / (n_raw * n_cooked)) - 1

        statistical_results.append({
            'macro_group': group,
            'nutrient': nutrient,
            'raw_n': n_raw,
            'cooked_n': n_cooked,
            'raw_median': raw_med,
            'cooked_median': cooked_med,
            'median_difference': med_diff,
            'u_statistic': u_stat,
            'p_value': p_val,
            'effect_size': rank_biserial
        })

results_df = pd.DataFrame(statistical_results)

# Apply Benjamini-Hochberg FDR correction
results_df['p_adjusted'] = multipletests(results_df['p_value'], method='fdr_bh')[1]
results_df['significant'] = results_df['p_adjusted'] < 0.05
results_df['direction'] = np.where(
    results_df['median_difference'] > 0, 'Cooked > Raw',
    np.where(results_df['median_difference'] < 0, 'Raw > Cooked', 'No difference')
)


# ==============================================================================
# STEP 6: DATASET EXPORTS FOR VISUALIZATION & REPORTING
# ==============================================================================

# 1. Main Dataset (Wide Format for Primary Analytics & Dashboards)
df_engineered.to_csv('final_food_dataset_tableau.csv', index=False, encoding='utf-8')

# 2. Reshaped Dataset (Long Format for Multi-Nutrient Comparison Visualizations)
id_cols = ['fdc_id', 'description', 'macro_group', 'processing_type']
food_nutrients_long = df_engineered[id_cols + nutrient_cols].melt(
    id_vars=id_cols,
    value_vars=nutrient_cols,
    var_name='nutrient',
    value_name='value'
).dropna(subset=['value']).reset_index(drop=True)

food_nutrients_long.to_csv('food_nutrients_long.csv', index=False, encoding='utf-8')

# 3. Statistical Analysis Output
results_df.to_csv('statistical_analysis_results.csv', index=False, encoding='utf-8')

# 4. Nutrient Metadata Lookup Table
nutrient_metadata = pd.DataFrame([
    ['calories_kcal', 'Calories', 'Energy', 'Lower', True],
    ['protein_g', 'Protein', 'Macronutrients', 'Higher', True],
    ['fat_g', 'Total Fat', 'Macronutrients', 'Neutral', True],
    ['carbs_g', 'Carbohydrates', 'Macronutrients', 'Neutral', True],
    ['fiber_g', 'Fiber', 'Macronutrients', 'Higher', True],
    ['water_g', 'Water', 'Other', 'Higher', False],
    ['sugars_g', 'Sugars', 'Sugars & Fats', 'Lower', True],
    ['saturated_fat_g', 'Saturated Fat', 'Sugars & Fats', 'Lower', True],
    ['trans_fat_g', 'Trans Fat', 'Sugars & Fats', 'Lower', True],
    ['cholesterol_mg', 'Cholesterol', 'Sugars & Fats', 'Lower', False],
    ['calcium_mg', 'Calcium', 'Minerals', 'Higher', True],
    ['iron_mg', 'Iron', 'Minerals', 'Higher', True],
    ['magnesium_mg', 'Magnesium', 'Minerals', 'Higher', True],
    ['phosphorus_mg', 'Phosphorus', 'Minerals', 'Higher', False],
    ['potassium_mg', 'Potassium', 'Minerals', 'Higher', True],
    ['sodium_mg', 'Sodium', 'Minerals', 'Lower', True],
    ['zinc_mg', 'Zinc', 'Minerals', 'Higher', True],
    ['vitamin_a_mcg', 'Vitamin A', 'Vitamins', 'Higher', True],
    ['vitamin_c_mg', 'Vitamin C', 'Vitamins', 'Higher', True],
    ['vitamin_b6_mg', 'Vitamin B6', 'B Vitamins', 'Higher', True],
    ['vitamin_b12_mcg', 'Vitamin B12', 'B Vitamins', 'Higher', True],
    ['vitamin_d_mcg', 'Vitamin D', 'Vitamins', 'Higher', True],
    ['vitamin_e_mg', 'Vitamin E', 'Vitamins', 'Higher', True],
    ['caffeine_mg', 'Caffeine', 'Other', 'Neutral', False],
    ['ash_g', 'Ash', 'Other', 'Neutral', False]
], columns=['nutrient', 'display_name', 'group', 'direction', 'use_in_score'])

nutrient_metadata.to_csv('nutrient_metadata.csv', index=False, encoding='utf-8')
