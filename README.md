# 📦 Inventory Intelligence Platform
### *Enterprise Demand Analytics, Stock-Out Risk & Inventory Optimization Engine*

---

## 🎯 Problem Statement
> **"Inventory Analytics: Analyze product demand and identify stock-out, overstock and slow-moving inventory."**

Retailers and supply chain organizations struggle with two costly extremes:
1. **Stock-Outs:** Depleted inventory leads to lost revenue, delayed customer fulfillment, and customer churn.
2. **Overstock & Sluggish Inventory:** Excess inventory ties up vital working capital, inflates warehouse holding costs, and risks permanent depreciation or obsolescence.

The **Inventory Intelligence Platform** bridges this gap by transforming raw transaction logs and stock levels into automated, explainable replenishment decisions and predictive demand forecasts.

---

## 🚀 Key Features

* **Flexible Column Auto-Discovery:** Seamlessly maps arbitrary dataset column headers (`Units_Sold`, `Qty`, `Sales`, `Current_Stock`, `On_Hand`, `Date`, `SKU`, etc.) into an internal standardized analytical schema without requiring manual reformatting.
* **Automated Data Hygiene & Preprocessing:** Handles whitespace, casing inconsistencies, duplicate records, missing prices/costs, negative quantities, and unparseable dates with a 100% transparent audit log.
* **Core Inventory Analytics Engine:**
  * Average Daily Demand ($\text{Total Demand} / \text{Days}$)
  * Safe Days of Inventory Remaining ($\text{Current Stock} / \text{Daily Demand}$)
  * Stock Coverage & Lead Time Gap Analysis
  * Dynamic Reorder Points ($\text{Daily Demand} \times \text{Lead Time} + \text{Safety Stock}$)
  * Daily Inventory Turnover Velocity & Consumption Rate
* **Objective Inventory Classification:**
  * 🔴 **STOCK-OUT / CRITICAL:** Zero stock on hand or coverage $\le 3$ days.
  * 🟡 **LOW STOCK:** Coverage $\le 7$ days or stock $\le$ Reorder Point.
  * 🟢 **HEALTHY:** Optimal balance between demand velocity and supplier lead times.
  * 🔵 **OVERSTOCK:** Coverage $> 60$ days, exposing excess inventory units and tied-up capital.
  * 🟣 **SLOW-MOVING:** Daily sales velocity $< 1.0$ unit/day with $> 30$ days of stagnant coverage.
* **Transparent Multi-Factor Risk Scoring (0–100):**
  * Evaluates stock-out vulnerability based on **Coverage Urgency** (40%), **Depletion Proximity** (25%), **Demand Acceleration** (20%), and **Supplier Lead Time Exposure** (15%).
  * Categorizes products into **Critical** (81–100), **High Risk** (61–80), **Medium Risk** (31–60), and **Low Risk** (0–30).
* **Explainable Procurement Recommendations:**
  * Generates concrete operational directives (e.g., *"Prioritize Urgent Replenishment"*, *"Halt Replenishment & Stimulate Demand"*, *"Review Purchasing & Markdown"*) backed by data-driven rationales and quantified financial impact.
* **Lightweight Machine Learning Demand Forecasting:**
  * Ensemble model blending **Linear Trend Regression**, **7-day Rolling Moving Averages**, and **Calendar Seasonality**.
  * Out-of-sample backtest validation with genuine **MAE** (Mean Absolute Error) and **RMSE** (Root Mean Squared Error) metrics—no fabricated accuracy.
* **Power BI & Analytics Ready Exports:**
  * Generates 4 clean, denormalized analytical CSV tables ready for Power BI, Tableau, or Excel ingestion.
* **Interactive Streamlit Executive Dashboard:**
  * 5 comprehensive pages featuring responsive Plotly visuals, interactive filters, real-time threshold adjustments, and drag-and-drop custom dataset uploader.

---

## 🏗️ Architecture & Project Structure

```text
inventory-analytics/
│
├── app.py                      # Commercial-grade Streamlit web application
├── requirements.txt            # Python dependencies (local, no paid APIs)
├── README.md                   # Comprehensive documentation & methodology
├── .gitignore                  # Git hygiene configuration
│
├── data/
│   ├── raw/                    # Raw source dataset (untouched)
│   └── processed/              # Cleaned standardized working dataset
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Documented operational thresholds & color constants
│   ├── data_loader.py          # Auto-discovery column mapper & data profiler
│   ├── preprocessing.py        # Data cleaning, deduplication & audit pipeline
│   ├── analytics.py            # Core analytics, coverage & classification engine
│   ├── risk_engine.py          # 0-100 Multi-factor Inventory Risk Scorer
│   ├── recommendations.py      # Explainable recommendation generator
│   ├── forecasting.py          # ML trend & time-series demand forecasting
│   └── export_engine.py        # Power BI analytical CSV export generator
│
├── exports/                    # Power BI-ready CSV analytical tables
│   ├── inventory_summary.csv
│   ├── product_risk.csv
│   ├── demand_trends.csv
│   └── category_summary.csv
│
├── tests/                      # Automated unit test suite
│   ├── test_preprocessing.py   # Hygiene, casing, whitespace, duplicate tests
│   ├── test_analytics.py       # Safe division, velocity & classification tests
│   └── test_risk_engine.py     # Risk score bounds (0-100) & factor tests
│
└── scripts/
    ├── generate_dataset.py     # Benchmark retail transaction generator
    └── test_pipeline.py        # End-to-end pipeline verification script
```

---

## 🔬 Analytics Methodology

### 1. Daily Demand & Stock Coverage
$$\text{Average Daily Demand} = \frac{\sum \text{Units Sold}}{\text{Active Days}}$$

$$\text{Days of Inventory Remaining} = \begin{cases} \frac{\text{Current Stock}}{\text{Average Daily Demand}} & \text{if } \text{Daily Demand} > 0 \\ 999.0 & \text{if } \text{Daily Demand} = 0 \text{ and } \text{Stock} > 0 \\ 0.0 & \text{if } \text{Stock} \le 0 \end{cases}$$

### 2. Dynamic Reorder Point
$$\text{Reorder Point (ROP)} = (\text{Average Daily Demand} \times \text{Lead Time Days}) + \text{Safety Stock}$$
*If supplier lead time or safety stock is missing from the dataset, the system applies transparent operational defaults ($14$ days lead time, $5$ days buffer) and labels them as estimated.*

### 3. Excess Inventory & Trapped Capital
$$\text{Expected Demand Horizon} = \text{Average Daily Demand} \times \text{OVERSTOCK\_DAYS}$$
$$\text{Excess Inventory Units} = \max(0, \text{Current Stock} - \text{Expected Demand Horizon})$$
$$\text{Overstock Value} = \text{Excess Inventory Units} \times \text{Unit Cost}$$

---

## 📊 Inventory Classification Logic

| Status | Trigger Condition | Operational Action |
| :--- | :--- | :--- |
| **STOCK-OUT / CRITICAL** | $\text{Current Stock} = 0 \lor \text{Days of Inventory} \le 3$ | Prioritize emergency expedited replenishment |
| **LOW STOCK** | $\text{Days of Inventory} \le 7 \lor \text{Current Stock} \le \text{ROP}$ | Place standard purchase order |
| **HEALTHY** | Stock aligned with lead time and safety buffer | Maintain scheduled monitoring |
| **OVERSTOCK** | $\text{Days of Inventory} > 60$ | Pause purchasing; explore promotional bundles |
| **SLOW-MOVING** | $\text{Daily Demand} < 1.0 \text{ unit/day} \land \text{Days} \ge 30$ | Reposition merchandise or run markdown tests |

---

## 📈 Power BI Integration (`exports/`)

The application automatically produces four analytical tables ready for Power BI:
1. `inventory_summary.csv`: Complete product catalog with stock, velocity, turnover, and excess metrics.
2. `product_risk.csv`: Product-level risk scores, factor penalties, and reorder urgency.
3. `demand_trends.csv`: Granular daily sales transactions by SKU and category.
4. `category_summary.csv`: Aggregated department-level inventory valuation and status counts.

---

## 💻 Installation & Local Execution

This application operates **100% locally** without external paid APIs (no OpenAI, Gemini, or Claude API required).

### Prerequisites
* Python 3.9+ (Tested on Python 3.13)
* Windows PowerShell or Command Prompt

### Step 1: Clone or Navigate to Directory
```powershell
cd c:\Users\bokka\OneDrive\Desktop\Inventory-Analytics-Hackathon
```

### Step 2: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Run the Streamlit Dashboard
```powershell
streamlit run app.py
```
*The interactive dashboard will automatically open at `http://localhost:8501`.*

---

## 🧪 Running Unit Tests
To verify data preprocessing, analytics, and risk scoring logic:
```powershell
python -m pytest tests/ -v
```

---

## 🔮 Future Roadmap & Enhancements
1. **Multi-Warehouse Geospatial Allocation:** Optimize stock transfers between regional distribution hubs.
2. **Supplier Lead Time Variability Modeling:** Incorporate Monte Carlo simulation for supplier delay distributions.
3. **Automated Purchase Order Generation:** One-click ERP export (SAP / NetSuite compatible CSV/EDI formats).
