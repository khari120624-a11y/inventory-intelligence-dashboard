"""
Export Engine for Power BI and Analytics Workflows.
Generates clean, denormalized analytical CSV tables ready for Power BI, Tableau, or Excel ingestion.
"""

import os
from typing import Dict, Any, List
import pandas as pd

def generate_powerbi_exports(
    prod_analytics: pd.DataFrame,
    clean_transactions: pd.DataFrame,
    cat_summary: pd.DataFrame,
    export_dir: str = "exports"
) -> Dict[str, str]:
    """
    Produces standard Power BI-ready CSV tables:
    1. inventory_summary.csv
    2. product_risk.csv
    3. demand_trends.csv
    4. category_summary.csv
    """
    os.makedirs(export_dir, exist_ok=True)
    generated_files = {}

    # 1. inventory_summary.csv
    inv_summary_cols = [
        "sku", "product_name", "category", "current_stock", "total_demand",
        "avg_daily_demand", "days_of_inventory", "inventory_status",
        "movement_class", "demand_trend", "trend_pct", "unit_cost",
        "unit_price", "inventory_value", "excess_inventory", "overstock_value",
        "reorder_point", "lead_time_days", "safety_stock", "recommended_action"
    ]
    avail_inv_cols = [c for c in inv_summary_cols if c in prod_analytics.columns]
    inv_summary_df = prod_analytics[avail_inv_cols].copy()
    p1 = os.path.join(export_dir, "inventory_summary.csv")
    inv_summary_df.to_csv(p1, index=False)
    generated_files["inventory_summary"] = p1

    # 2. product_risk.csv
    risk_cols = [
        "sku", "product_name", "category", "inventory_risk_score", "risk_tier",
        "days_of_inventory", "current_stock", "avg_daily_demand", "reorder_point",
        "lead_time_days", "risk_coverage_score", "risk_depletion_score",
        "risk_trend_score", "risk_lead_time_score", "recommended_action", "recommendation_rationale"
    ]
    avail_risk_cols = [c for c in risk_cols if c in prod_analytics.columns]
    product_risk_df = prod_analytics[avail_risk_cols].copy()
    p2 = os.path.join(export_dir, "product_risk.csv")
    product_risk_df.to_csv(p2, index=False)
    generated_files["product_risk"] = p2

    # 3. demand_trends.csv
    if not clean_transactions.empty and "date" in clean_transactions.columns:
        demand_trends_df = (
            clean_transactions.groupby(["date", "category", "sku", "product_name"])
            .agg(units_sold=("units_sold", "sum"))
            .reset_index()
        )
    else:
        demand_trends_df = pd.DataFrame()
    p3 = os.path.join(export_dir, "demand_trends.csv")
    demand_trends_df.to_csv(p3, index=False)
    generated_files["demand_trends"] = p3

    # 4. category_summary.csv
    p4 = os.path.join(export_dir, "category_summary.csv")
    cat_summary.to_csv(p4, index=False)
    generated_files["category_summary"] = p4

    return generated_files
