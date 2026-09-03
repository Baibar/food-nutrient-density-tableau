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

## 🔍 Data Quality & Outlier Detection (IQR Analysis)

To evaluate dataset distribution and identifying extreme values across $7,017$ food items, an Interquartile Range (IQR) analysis was performed:

$$\text{IQR} = Q_3 - Q_1$$
$$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}, \quad \text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$

### Key Outlier Distribution Findings

| Nutrient Metric | Outliers Detected (out of 7,017) | Lower Bound | Upper Bound | Domain Interpretation |
| :--- | :---: | :---: | :---: | :--- |
| **`calories_kcal`** | **154** (2.2%) | -233.50 | 650.50 | Concentrated fats/oils (pure butter, lard) exceed energy bounds naturally. |
| **`protein_g`** | **30** (0.4%) | -25.93 | 49.64 | Highly stable metric. Pure protein powders and isolates drive high values. |
| **`fat_g`** | **436** (6.2%) | -19.00 | 33.80 | Skewed by vegetable oils, nuts, and high-fat dairy spreads. |
| **`carbs_g`** | **641** (9.1%) | -41.40 | 69.00 | Pure sugars, starches, and refined flour products trigger thresholds. |
| **`sugars_g`** | **753** (10.7%) | -9.95 | 16.57 | Confectionery, syrups, and dried fruits naturally exceed limits. |
| **`vitamin_c_mg`** | **1,213** (17.3%) | -3.60 | 6.00 | Most foods contain ~0 mg, making citrus fruits and bell peppers statistical outliers. |
| **`vitamin_b12_mcg`** | **1,206** (17.2%) | -0.45 | 0.75 | Highly skewed toward organ meats (liver) and specific seafood. |
| **`water_g`** | **0** (0.0%) | -20.80 | 134.40 | Perfectly distributed across all food items with zero extreme violations. |
| **`caffeine_mg`** | **274** (3.9%) | 0.00 | 0.00 | $Q_1, Q_3$, and median are all 0; any caffeine-containing item (coffee, tea) is flagged. |

### Data Cleaning Strategy for Outliers
1. **No Hard Truncation:** Outliers were **not removed** indiscriminately, as extreme values represent valid biological variability (e.g., pure oil *should* have ~900 kcal/100g).
2. **Capping for Scoring:** For composite metrics like the **Nutrient Density Index (NDI)**, nutrient values were capped at **200% Daily Value (DV)** to prevent single extreme vitamins (e.g., Vitamin C in acerola) from distorting total food rankings.
3. **Non-Parametric Testing:** Due to extreme right-skewness identified during IQR analysis, non-parametric tests (**Mann-Whitney U** and **Kruskal-Wallis**) were chosen over parametric ANOVA/t-tests.

## 🔗 Nutrient Correlation Analysis (Spearman Rank Correlation)

To evaluate non-linear and non-normally distributed relationships between nutritional variables, **Spearman’s rank correlation coefficient ($\rho$)** was calculated across all key micro- and macro-nutrients.

$$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$

### Key Correlation Matrix Insights

#### 🔝 Top 5 Positive Correlations

| Variable A | Variable B | $\rho$ (Spearman) | Domain Interpretation & Biological Drivers |
| :--- | :--- | :---: | :--- |
| **`fat_g`** | **`saturated_fat_g`** | **+0.958** | Near-linear relationship; saturated fats form the primary structural backbone of dietary fats. |
| **`zinc_mg`** | **`protein_g`** | **+0.849** | Strong bio-co-occurrence; animal proteins and whole legumes serve as primary dual matrices for both. |
| **`carbs_g`** | **`sugars_g`** | **+0.831** | Simple sugars form a major sub-category of total carbohydrates in fruits and processed foods. |
| **`protein_g`** | **`phosphorus_mg`** | **+0.801** | High organic linkage; phosphorus is bound within phosphoproteins in meat, dairy, and eggs. |
| **`trans_fat_g`** | **`saturated_fat_g`** | **+0.785** | Shared technological processing (e.g., partial hydrogenation in bakery/frying fats). |

---

#### 🔻 Top 5 Negative Correlations

| Variable A | Variable B | $\rho$ (Spearman) | Domain Interpretation & Biological Drivers |
| :--- | :--- | :---: | :--- |
| **`water_g`** | **`calories_kcal`** | **-0.967** | Inverse density effect; water acts as a natural volumetric diluent, drastically reducing caloric density. |
| **`fiber_g`** | **`cholesterol_mg`** | **-0.686** | Strict plant vs. animal origin dichotomy (dietary fiber exists solely in plants, cholesterol solely in animal sources). |
| **`cholesterol_mg`** | **`carbs_g`** | **-0.664** | Animal-based foods high in cholesterol naturally lack complex plant carbohydrates. |
| **`fat_g`** | **`water_g`** | **-0.647** | Hydrophobic displacement; lipid-rich matrices (oils, butter) displace moisture during processing/nature. |
| **`sugars_g`** | **`cholesterol_mg`** | **-0.613** | Separate food profiles; high-sugar items (fruits, sweets) originate from plants and lack animal cholesterol. |

---

### 💡 Analytical Takeaways for Dashboard & Modeling
1. **Multicollinearity Awareness:** Due to high correlation ($\rho > 0.80$), metrics like `saturated_fat_g` vs. `fat_g` or `phosphorus_mg` vs. `protein_g` should be monitored to prevent feature redundancy in regression or clustering models.
2. **Nutrient Density Index (NDI) Calibration:** The strong inverse relationship between `water_g` and `calories_kcal` ($\rho = -0.967$) confirms that water-rich whole foods (fruits, vegetables) naturally score higher in volume-to-calorie nutritional density

## 🧪 Statistical Hypothesis Testing (Mann-Whitney U & FDR Correction)

To statistically evaluate whether thermal processing and cooking methods significantly alter nutrient concentrations across macro groups, non-parametric **Mann-Whitney U tests** were conducted ($N = 83$ statistically significant pairwise combinations identified).

To eliminate Type I errors (false positives) arising from multiple testing, the **Benjamini-Hochberg False Discovery Rate (FDR)** procedure was applied:

$$\text{FDR Threshold: } p_{\text{adjusted}} < 0.05$$

The magnitude of nutritional change was quantified using **Rank-Biserial Correlation ($r_{rb}$)** Effect Size:
* **Large Effect:** $|r_{rb}| \ge 0.50$
* **Medium Effect:** $0.30 \le |r_{rb}| < 0.50$
* **Small / Negligible:** $|r_{rb}| < 0.30$

---

### 📌 Top Statistically Significant Findings

#### 1. Major Nutritional Shifts (Large Effect Size)
Cooking causes significant moisture loss, leading to a concentrated density of proteins and minerals in cooked food matrices:

| Macro Group | Nutrient Metric | Raw Median | Cooked Median | Median Diff | $p_{\text{adjusted}}$ | Effect Size ($r_{rb}$) | Direction & Interpretation |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Meat & Poultry** | `protein_g` | 20.20 g | 26.60 g | **+6.40 g** | $2.20 \times 10^{-17}$ | **0.69** | **Cooked > Raw (Large):** Water evaporation during cooking increases protein concentration per 100g. |
| **Meat & Poultry** | `water_g` | 70.80 g | 60.70 g | **-10.10 g** | $8.72 \times 10^{-139}$ | **0.62** | **Raw > Cooked (Large):** Direct thermal moisture loss during roasting, grilling, and frying. |
| **Seafood & Fish** | `ash_g` | 1.28 g | 1.67 g | **+0.39 g** | $2.40 \times 10^{-16}$ | **0.62** | **Cooked > Raw (Large):** Mineral retention after liquid loss increases total ash percentage. |
| **Seafood & Fish** | `water_g` | 78.00 g | 70.00 g | **-8.00 g** | $1.59 \times 10^{-15}$ | **0.60** | **Raw > Cooked (Large):** Significant dehydration during cooking processes. |
| **Seafood & Fish** | `protein_g` | 18.40 g | 22.90 g | **+4.50 g** | $6.76 \times 10^{-14}$ | **0.57** | **Cooked > Raw (Large):** Structural protein concentration per 100g sample. |

---

#### 2. Technically Significant but Practically Negligible Shifts
Large sample sizes ($N > 1,000$) can produce extremely small $p$-values even for minor absolute differences. Evaluating **Effect Size** prevents false business conclusions:

| Macro Group | Nutrient Metric | Raw Median | Cooked Median | Median Diff | $p_{\text{adjusted}}$ | Effect Size ($r_{rb}$) | Practical Takeaway |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Meat & Poultry** | `potassium_mg` | 297.0 mg | 300.0 mg | +3.0 mg | 0.0305 | **0.061** | **Negligible:** Minor concentration shift; negligible nutritional difference in dietary planning. |
| **Fruits** | `trans_fat_g` | 0.00 g | 0.00 g | 0.00 g | 0.0448 | **0.052** | **No Difference:** Trace additions in specific processed fruit products do not shift fruit category profile. |
| **Vegetables & Legumes**| `vitamin_b12_mcg`| 0.00 mcg | 0.00 mcg | 0.00 mcg | 0.0039 | **0.050** | **No Difference:** Plants inherently lack B12; minor traces in prepared dishes reflect fortified additives. |
| **Meat & Poultry** | `fiber_g` | 0.00 g | 0.00 g | 0.00 g | 0.0072 | **0.019** | **No Difference:** Meat products remain zero-fiber foods regardless of thermal processing state. |

---

### 💡 Key Takeaways for Analytical Dashboard
1. **The Concentration Effect:** The observed increase in nutrients like `protein_g` or `ash_g` during cooking is primarily driven by **water loss (`water_g` reduction)** rather than nutrient synthesis.
2. **Methodological Rigor:** By pairing $p$-value adjustments (Benjamini-Hochberg) with **Rank-Biserial Effect Sizes**, we filter out statistical noise and focus dashboard insights strictly on impactful nutritional shifts ($|r_{rb}| \ge 0.30$).
