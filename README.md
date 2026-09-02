# 🥗 USDA Food Nutrient Analysis & Quality Ranking Dashboard

An interactive Tableau dashboard that provides an objective, data-driven assessment of food products based on their nutrient composition. The project transforms USDA long-format data into a flexible scoring system using percentile ranking, conditional inversion for limit nutrients, and dynamic table calculations.

🔗 **[View Interactive Dashboard on Tableau Public](#)** *(Вставити лінк на Tableau Public)*

---

## 📌 Executive Summary

Evaluating food items purely by raw values (e.g., milligrams of sodium vs. grams of protein) is challenging due to varying units and health impacts. This project solves this by:
1. **Normalizing Nutrient Values:** Converting raw metrics per 100g into relative percentiles across the dataset.
2. **Accounting for Health Impact:** Inverting rank percentiles for "limit nutrients" (Sugar, Sodium, Cholesterol, Saturated/Trans Fats) so that lower levels yield healthier scores.
3. **Dynamic Multi-Nutrient Scoring:** Allowing users to select any combination of nutrients to calculate a dynamic **Combined Score** and rank products in real time.

---

## 🛠 Features & Analytical Methodology

* **Three-Layer Nested Table Calculations:**
  * **`Adjusted Nutrient Percentile`**: Calculates `RANK_PERCENTILE` for each nutrient across products. Inverts the logic (`1 - RANK_PERCENTILE`) for harmful nutrients.
  * **`Combined Score`**: Computes `WINDOW_SUM` of selected nutrient percentiles for each product.
  * **`Combined Rank`**: Applies `RANK(..., 'desc')` to sort products dynamically based on user-selected filters.
* **Cascading Categorical Filters:** Hierarchical filtering (`Macro Group` $\rightarrow$ `Category` $\rightarrow$ `Nutrient`) configured with `Only Relevant Values` to prevent empty selections.
* **Non-Conflicting Top-N Filtering:** Custom table calculation filter (`[Combined Rank] <= 15`) ensuring Top 15 displays operate seamlessly after table calculations execute.
* **Clear Visual UX:** Informative tooltips clarifying the per 100g evaluation basis and inverted scoring logic.

---

## 📊 Dataset Overview

* **Source:** USDA FoodData Central (FDC)
* **Structure:** Long Format (Tidy Data)
* **Primary Fields:** `description` (Food Item), `category`, `macro_group`, `nutrient`, `value` (per 100g basis)

---

## 💻 Tech Stack & Tools

* **Visualization:** Tableau Desktop / Tableau Public
* **Data Processing & Analytics:** Advanced Table Calculations, Level-of-Detail (LOD) Expressions, Discrete Sorting Architecture
* **Dataset Management:** Long-format mapping & SQL/Python preprocessing

---
