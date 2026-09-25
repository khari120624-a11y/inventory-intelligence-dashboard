# 🎤 3-Minute Hackathon Pitch Deck & Script
## Project: Inventory Intelligence Platform
**Presenter:** Hackathon Team  
**Duration:** 3 Minutes  
**Focus:** Demand Analytics, Stock-Out Risk, Overstock Optimization & Explainable Decision-Making

---

### [0:00 - 0:35] Slide 1: The Multi-Billion Dollar Inventory Dilemma (The Problem)

> *"Good morning judges and mentors. In retail and supply chain operations, businesses bleed cash from two opposing extremes:*
> 1. ***Stock-Outs:*** *When a best-seller runs out of stock, revenue stops immediately and customers defect to competitors.*
> 2. ***Overstock & Sluggish Inventory:*** *Excess goods sit silently in warehouses, tying up working capital, accumulating storage fees, and risking obsolescence.*
>
> *Today, most operations teams rely on static, fragmented spreadsheets or gut feeling. They discover a stock-out after orders fail, and they notice overstock only during end-of-year tax write-offs.*
>
> *We built **Inventory Intelligence** to turn passive inventory logs into active, automated decision-making."*

---

### [0:35 - 1:15] Slide 2: The Solution & Technical Architecture

> *"Our platform ingests raw transactional demand and inventory feeds and automates the entire supply chain intelligence workflow:*
>
> 1. ***Intelligent Auto-Mapping:*** *It automatically discovers and normalizes arbitrary column names—whether your data calls it `Qty`, `Units_Sold`, or `Current_Stock`—with zero manual data reformatting.*
> 2. ***Transparent Preprocessing Engine:*** *It deduplicates records, standardizes inconsistent category casing, imputes missing prices using median category ratios, and clips anomalous negative quantities.*
> 3. ***Core Analytics & Coverage Engine:*** *Computes Average Daily Demand, safe Days of Inventory Remaining, dynamic Reorder Points, and consumption velocity.*
> 4. ***0–100 Multi-Factor Risk Scorer:*** *Quantifies stock-out vulnerability based on coverage urgency relative to supplier lead times, depletion proximity, and demand acceleration.*
> 5. ***Explainable Recommendations:*** *Generates concrete procurement directives with clear data-backed explanations.*
>
> *Best of all: It operates **100% locally** without external paid APIs, ensuring total data privacy and zero vendor lock-in."*

---

### [1:15 - 2:20] Slide 3: Live Dataset Demonstration & Real Findings

> *"Let’s inspect what our system uncovered from 5,400 transactional records across 180 days of operations:*
>
> * **Overall Volume:** We analyzed **30 SKUs** holding **3,954 inventory units** worth **$182,595** in working capital, supporting **20,088 total units demanded**.
> * **Top Demand Driver:** **Wireless Noise-Canceling Headphones (SKU-ELC-001)** led the business with **2,052 units sold** (averaging 11.4 units/day), making **Electronics** the highest-demand category with **6,621 total units**.
> * **Imminent Stock-Out Risk:** We identified **7 critical products**. Most urgently, the **Electric Precision Milk Frother** is already at **0 units on hand** (completely stocked out). Meanwhile, **Seamless Compression Leggings** (4 units left, 0.4 days coverage) and the top-selling **Wireless Headphones** (12 units left, 1.1 days coverage) will exhaust stock in roughly 24 hours—far shorter than the 14-day supplier lead time.
> * **Working Capital Trapped in Overstock:** **5 products** exceed 60 days of coverage, tying up **$126,566.80** in excess inventory capital! The **4K Action Camera** alone has 420 units on hand ($40,508 trapped), while the **Arctic Winter Parka** has 510 units ($34,510 trapped).
> * **Slow-Moving Inventory:** **5 SKUs** have stagnated at less than 0.20 units sold per day—including the **Cast Iron Dutch Oven** (0.089 units/day with 140 units on hand).
> * **Predictive Forecasting:** In our Product Explorer, we provide out-of-sample validated demand forecasting (Linear Trend + 7-Day Rolling Moving Average + Calendar Seasonality) with verifiable backtest MAE and RMSE metrics."*

---

### [2:20 - 3:00] Slide 4: Business Impact & Executive ROI

> *"The business impact of this platform is direct, measurable, and immediate:*
>
> 1. ***Eliminates Stock-Out Losses:*** *Triggers proactive purchase orders before products breach supplier lead times, saving an estimated 15–25% in lost sales.*
> 2. ***Unlocks Working Capital:*** *Immediately highlights **$126.5k in trapped overstock cash**, enabling leadership to pause purchase orders and launch promotional bundles.*
> 3. ***Bridges the BI Gap:*** *Exports 4 clean, denormalized tables directly into **Power BI and Tableau** for enterprise reporting.*
> 4. ***Explainable Procurement Directives:*** *Purchasing teams receive not just a number, but the exact rationale: 'Reorder recommended because current inventory covers only 1.1 days of demand against a 14-day supplier cycle.'*
>
> *Inventory Intelligence turns messy retail logs into profitable supply chain clarity. Thank you, and we welcome your questions!"*

---

### 📋 Rapid Data Summary Cheat Sheet for Judges

| Metric | Exact Ground-Truth Dataset Value |
| :--- | :--- |
| **Analyzed SKUs / Products** | 30 products across 5 categories |
| **Total Inventory On Hand** | 3,954 units |
| **Total Working Capital Tied Up** | $182,595.00 |
| **Total Units Demanded (180 Days)** | 20,088 units |
| **Top Demand Category** | **Electronics** (6,621 units demanded) |
| **Top Demand Product** | **Wireless Noise-Canceling Headphones** (2,052 units sold) |
| **Critical Stock-Out SKUs** | **7 products** (Milk Frother at 0 units; Leggings at 4 units; Headphones at 12 units) |
| **Overstocked SKUs** | **5 products** (Action Camera, Parka, Resistance Bands, etc.) |
| **Trapped Capital in Excess Stock** | **$126,566.80** |
| **Slow-Moving SKUs** | **5 products** (Dutch Oven, Turntable, Blazer, Diffuser, Tent) |
| **ML Forecast Validation** | Out-of-sample backtested MAE & RMSE with 80% confidence bands |
| **Power BI Exports** | `inventory_summary.csv`, `product_risk.csv`, `demand_trends.csv`, `category_summary.csv` |
