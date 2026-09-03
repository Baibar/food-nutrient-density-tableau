# 🥗 USDA Food Nutrient Analysis

An interactive Tableau dashboard that provides an objective, data-driven assessment of food products based on their nutrient composition. The project transforms USDA long-format data into a flexible scoring system using percentile ranking, conditional inversion for limit nutrients, and dynamic table calculations.

🔗 **[View Interactive Dashboard on Tableau Public](#)**

---

An end-to-end Data Analytics project focused on extracting, cleaning, transforming, and categorizing large-scale complex nutritional data from the **USDA FoodData Central (SR Legacy)** dataset. 

This project transforms deeply nested raw JSON structures into a clean, normalized, and feature-engineered dataset ready for EDA, machine learning, and interactive Tableau dashboards.

---

## 📌 Project Overview

The primary goal of this repository is to establish a automated **ETL (Extract, Transform, Load)** pipeline for complex nutritional data. Raw nutritional databases often suffer from deep JSON nesting, heterogeneous unit measurements (e.g., mixing `IU` with `mcg`), high categorical noise (e.g., baby foods, fortified niche items), and a lack of standardized processing labels.

### Key Objectives:
* **Nested JSON Parsing:** Extract and flatten multi-level JSON structures for over 7,000+ food items and 148 distinct nutrients.
* **Data Standardisation & Unit Conversion:** Convert mixed measurement units (e.g., Vitamin A & D from `IU` to `mcg`) into uniform SI units.
* **Noise Reduction & Data Filtering:** Filter out non-general consumer items (baby formulas, restaurant meals, fortified supplements) to maintain analytical integrity.
* **Feature Engineering & Regex Classification:**
  * Categorize 20+ fine-grained USDA categories into **10 core Macro-Groups** (e.g., *Vegetables & Legumes*, *Meat & Poultry*, *Grains & Bakery*).
  * Build an advanced priority-based **Regex Engine** to classify processing levels into **`Raw / Whole Food`** vs. **`Cooked / Processed`**.
* **Statistical Outlier Detection:** Evaluate nutrient distributions and extreme values using the Interquartile Range (**IQR**) method.

---

## 🛠️ Tech Stack & Tools

* **Language:** Python 3.x
* **Data Manipulation & Parsing:** Pandas, NumPy, JSON library
* **Text Analysis & Regex:** Re (Regular Expressions), Collections (`Counter`)
* **Statistical Analysis & Viz:** SciPy, Seaborn, Matplotlib
* **Environment:** Google Colab / Jupyter Notebook
* **Downstream Visualization:** Tableau Public / Power BI

---

## 📐 Data Pipeline & Methodology

### 1. JSON Extraction & Flattening
Raw data contains nested dictionaries for each food item and its corresponding array of nutrients. Key metrics extracted:
* Core Attributes: `fdc_id`, `description`, `foodCategory`
* Macronutrients: Calories (`kcal`), Protein (`g`), Fat (`g`), Carbohydrates (`g`), Fiber (`g`), Sugars (`g`), Water (`g`), Ash (`g`)
* Micronutrients: Sodium, Potassium, Calcium, Iron, Magnesium, Vitamins (A, C, D, E, B6, B12), Cholesterol, Caffeine

### 2. Unit Harmonization
* **Vitamin A:** Harmonized Retinol Activity Equivalents (`RAE`) in `mcg`, converting legacy `IU` values where applicable (`1 IU ≈ 0.3 strictly RAE mcg`).
* **Vitamin D:** Standardized `IU` to `mcg` using the standard conversion factor (`1 mcg = 40 IU`).

### 3. Feature Engineering Logic
* **`macro_group`**: Mapping algorithm consolidating sparse categories into 10 key nutritional classes.
* **`processing_type`**: A multi-stage rule engine matching domain-specific text patterns:
  * Detects explicit raw indicators (`raw`, `fresh`, `unbaked`, `uncooked`).
  * Detects thermal/industrial processing (`cooked`, `boiled`, `roasted`, `canned`, `pasteurized`).
  * Accounts for implicitly processed goods (e.g., `bread`, `cookies`, `pretzels`, `chips`) while excluding raw dough/batter mixtures.

---

### 4. Data Quality Audit & Outlier Detection
* **Statistical Integrity:** Utilized Interquartile Range (IQR) analysis ($Q1 - 1.5 \times IQR$ to $Q3 + 1.5 \times IQR$) to identify extreme concentration levels across 25 target nutritional variables.
* **Density Validation:** Ensured logical consistency across macronutrient totals (e.g., verifying that the sum of protein, fat, carbohydrates, water, and ash aligns with standard 100g weight baselines).

---

## 📈 Key Insights & Target Analytical Use Cases

The refined dataset enables clear segmentation for downstream exploratory analysis and visualization:
* **Nutritional Density vs. Food Processing:** Comparing macronutrient profiles and caloric density between raw whole ingredients and processed consumer products.
* **Micronutrient Profiling:** Identifying high-yield sources of essential minerals (Iron, Calcium, Magnesium) and vitamins across different macro-groups.
* **Tableau / Power BI Dashboard Readiness:** Prepared optimized, flat tabular structures ideal for interactive filters, calculated fields (e.g., % of daily recommended values), and scatter plot matrix analysis.

---
