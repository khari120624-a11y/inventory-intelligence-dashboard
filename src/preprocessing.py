"""
Data Preprocessing and Data Hygiene Pipeline.
Cleans raw transactional and inventory data while recording a transparent audit log of all transformations.
"""

import os
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.config import DEFAULT_LEAD_TIME_DAYS, DEFAULT_SAFETY_STOCK_DAYS

def preprocess_inventory_data(
    raw_df: pd.DataFrame, 
    mapping: Dict[str, str]
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Cleans and standardizes raw DataFrame based on mapped column names.
    Returns cleaned DataFrame with canonical schema and an audit log of all cleaning operations.
    """
    audit_log = {
        "initial_rows": len(raw_df),
        "initial_cols": len(raw_df.columns),
        "duplicates_removed": 0,
        "whitespace_trimmed_cols": [],
        "categories_normalized": 0,
        "invalid_dates_handled": 0,
        "negative_quantities_corrected": 0,
        "missing_values_handled": {},
        "rows_after_cleaning": 0,
        "cleaning_decisions": []
    }

    df = raw_df.copy()

    # Step 1: Remove exact duplicate rows
    initial_dups = int(df.duplicated().sum())
    if initial_dups > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        audit_log["duplicates_removed"] = initial_dups
        audit_log["cleaning_decisions"].append(
            f"Removed {initial_dups} duplicate records to prevent double-counting of demand and stock."
        )

    # Step 2: Build standardized canonical dataframe
    standard_df = pd.DataFrame()

    # Product Identifier / SKU
    prod_col = mapping.get("sku") or mapping.get("product_name")
    if prod_col and prod_col in df.columns:
        standard_df["sku"] = df[prod_col].astype(str).str.strip()
    else:
        standard_df["sku"] = [f"SKU-{i:04d}" for i in range(len(df))]
        audit_log["cleaning_decisions"].append("Assigned synthetic SKU identifiers because no product identifier column was detected.")

    # Product Name
    name_col = mapping.get("product_name") or mapping.get("sku")
    if name_col and name_col in df.columns:
        standard_df["product_name"] = df[name_col].astype(str).str.strip()
    else:
        standard_df["product_name"] = standard_df["sku"]

    # Category
    cat_col = mapping.get("category")
    if cat_col and cat_col in df.columns:
        # Strip whitespace and capitalize words consistently
        cleaned_cat = df[cat_col].astype(str).str.strip().str.title()
        # Replace empty or 'Nan' strings with General
        cleaned_cat = cleaned_cat.replace({"Nan": "Uncategorized", "None": "Uncategorized", "": "Uncategorized"})
        standard_df["category"] = cleaned_cat
        audit_log["whitespace_trimmed_cols"].append(cat_col)
        audit_log["categories_normalized"] = int(cleaned_cat.nunique())
        audit_log["cleaning_decisions"].append("Standardized category casing and trimmed whitespace across category entries.")
    else:
        standard_df["category"] = "General Merchandise"
        audit_log["cleaning_decisions"].append("Assigned default category 'General Merchandise' as category column was not present.")

    # Date
    date_col = mapping.get("date")
    if date_col and date_col in df.columns:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
        nat_count = int(parsed_dates.isna().sum())
        if nat_count > 0:
            audit_log["invalid_dates_handled"] = nat_count
            # Forward-fill / back-fill or fill with min date to avoid dropping valuable demand records
            parsed_dates = parsed_dates.bfill().ffill().fillna(pd.Timestamp.now().normalize())
            audit_log["cleaning_decisions"].append(f"Imputed {nat_count} invalid/unparseable dates using temporal boundary fill.")
        standard_df["date"] = parsed_dates
    else:
        # Synthesize a single baseline date if date is absent
        standard_df["date"] = pd.Timestamp.now().normalize()
        audit_log["cleaning_decisions"].append("Dataset lacks date dimension; anchored transactions to current operational timestamp.")

    # Units Sold / Demand
    demand_col = mapping.get("units_sold")
    if demand_col and demand_col in df.columns:
        numeric_demand = pd.to_numeric(df[demand_col], errors="coerce").fillna(0)
        # Check negative quantities
        neg_count = int((numeric_demand < 0).sum())
        if neg_count > 0:
            numeric_demand = numeric_demand.clip(lower=0)
            audit_log["negative_quantities_corrected"] = neg_count
            audit_log["cleaning_decisions"].append(
                f"Clipped {neg_count} negative demand values to 0 (treated as returned/cancelled orders rather than negative consumption)."
            )
        standard_df["units_sold"] = numeric_demand.astype(float)
    else:
        standard_df["units_sold"] = 0.0
        audit_log["cleaning_decisions"].append("Demand column missing; initialized units_sold to 0.0.")

    # Current Stock
    stock_col = mapping.get("current_stock")
    if stock_col and stock_col in df.columns:
        numeric_stock = pd.to_numeric(df[stock_col], errors="coerce").fillna(0)
        neg_stock_count = int((numeric_stock < 0).sum())
        if neg_stock_count > 0:
            numeric_stock = numeric_stock.clip(lower=0)
            audit_log["cleaning_decisions"].append(f"Corrected {neg_stock_count} negative stock entries to 0.")
        standard_df["current_stock"] = numeric_stock.astype(float)
    else:
        standard_df["current_stock"] = 0.0
        audit_log["cleaning_decisions"].append("Stock column missing; initialized current_stock to 0.0.")

    # Unit Price
    price_col = mapping.get("unit_price")
    if price_col and price_col in df.columns:
        prices = pd.to_numeric(df[price_col], errors="coerce")
        missing_prices = int(prices.isna().sum())
        if missing_prices > 0:
            # Impute with product or category median, fallback to 10.0
            cat_median = prices.groupby(standard_df["category"]).transform("median")
            prices = prices.fillna(cat_median).fillna(prices.median() if not pd.isna(prices.median()) else 25.0)
            audit_log["missing_values_handled"]["unit_price"] = missing_prices
            audit_log["cleaning_decisions"].append(f"Imputed {missing_prices} missing unit price values using category median prices.")
        standard_df["unit_price"] = prices.round(2)
    else:
        standard_df["unit_price"] = 0.0

    # Unit Cost
    cost_col = mapping.get("unit_cost")
    if cost_col and cost_col in df.columns:
        costs = pd.to_numeric(df[cost_col], errors="coerce")
        missing_costs = int(costs.isna().sum())
        if missing_costs > 0:
            # Assume 50% of price if cost missing, or category median
            fallback_cost = standard_df["unit_price"] * 0.5
            costs = costs.fillna(fallback_cost).fillna(10.0)
            audit_log["missing_values_handled"]["unit_cost"] = missing_costs
            audit_log["cleaning_decisions"].append(f"Imputed {missing_costs} missing unit costs via industry gross-margin ratio (50% of price).")
        standard_df["unit_cost"] = costs.round(2)
    else:
        # Default cost estimated as 50% of unit price
        standard_df["unit_cost"] = (standard_df["unit_price"] * 0.5).round(2)
        audit_log["cleaning_decisions"].append("Estimated unit cost as 50% of unit price because cost column was not provided.")

    # Lead Time Days
    lt_col = mapping.get("lead_time_days")
    if lt_col and lt_col in df.columns:
        lead_times = pd.to_numeric(df[lt_col], errors="coerce").fillna(DEFAULT_LEAD_TIME_DAYS)
        standard_df["lead_time_days"] = lead_times.clip(lower=1).astype(int)
    else:
        standard_df["lead_time_days"] = DEFAULT_LEAD_TIME_DAYS
        audit_log["cleaning_decisions"].append(f"Applied transparent default lead time of {DEFAULT_LEAD_TIME_DAYS} days.")

    # Safety Stock
    safety_col = mapping.get("safety_stock")
    if safety_col and safety_col in df.columns:
        safeties = pd.to_numeric(df[safety_col], errors="coerce").fillna(0)
        standard_df["safety_stock"] = safeties.clip(lower=0).astype(int)
    else:
        standard_df["safety_stock"] = None  # Will be dynamically estimated in analytics if missing

    # Reorder Point
    rop_col = mapping.get("reorder_point")
    if rop_col and rop_col in df.columns:
        rops = pd.to_numeric(df[rop_col], errors="coerce").fillna(0)
        standard_df["reorder_point"] = rops.clip(lower=0).astype(int)
    else:
        standard_df["reorder_point"] = None  # Will be dynamically estimated in analytics

    # Step 3: Handle empty product names or invalid product identifiers
    valid_mask = standard_df["product_name"].notna() & (standard_df["product_name"] != "") & (standard_df["product_name"] != "nan")
    dropped_prods = int((~valid_mask).sum())
    if dropped_prods > 0:
        standard_df = standard_df[valid_mask].reset_index(drop=True)
        audit_log["cleaning_decisions"].append(f"Filtered out {dropped_prods} rows with missing product identifiers.")

    audit_log["rows_after_cleaning"] = len(standard_df)

    return standard_df, audit_log

def save_processed_data(df: pd.DataFrame, output_path: str = "data/processed/retail_inventory_cleaned.csv") -> str:
    """Saves cleaned DataFrame to processed directory."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path
