"""
Core Inventory Analytics Engine.
Calculates product, category, and time-level metrics:
- Stock coverage, average daily demand, velocity, days of inventory
- Reorder points, safety stock calculations (transparent defaults)
- Overstock excess metrics and valuations
- Slow-moving product movement diagnostics
- Inventory status classification
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.config import (
    CRITICAL_STOCKOUT_DAYS,
    LOW_STOCK_DAYS,
    OVERSTOCK_DAYS,
    SLOW_MOVING_DAYS,
    DEFAULT_LEAD_TIME_DAYS,
    DEFAULT_SAFETY_STOCK_DAYS,
    STATUS_CRITICAL,
    STATUS_LOW_STOCK,
    STATUS_HEALTHY,
    STATUS_OVERSTOCK,
    STATUS_SLOW_MOVING,
    ALL_STATUSES
)

def compute_product_analytics(
    df: pd.DataFrame,
    low_stock_days: float = LOW_STOCK_DAYS,
    overstock_days: float = OVERSTOCK_DAYS,
    slow_moving_days: float = SLOW_MOVING_DAYS,
    critical_days: float = CRITICAL_STOCKOUT_DAYS
) -> pd.DataFrame:
    """
    Computes complete product-level inventory analytics, stock coverage, reorder points,
    excess stock, and inventory classification.
    """
    if df.empty:
        return pd.DataFrame()

    # Determine date span
    has_date = "date" in df.columns and not df["date"].isna().all()
    if has_date:
        min_date = df["date"].min()
        max_date = df["date"].max()
        total_days = max(1, (max_date - min_date).days + 1)
    else:
        total_days = 30  # Standard monthly operational baseline
        min_date = None
        max_date = None

    product_records = []

    # Group by SKU / Product
    grouped = df.groupby(["sku", "product_name", "category"])

    for (sku, prod_name, cat), group in grouped:
        total_demand = float(group["units_sold"].sum())
        
        # Unique days active for this product
        prod_days = group["date"].nunique() if has_date else total_days
        effective_days = max(1, prod_days)
        
        avg_daily_demand = round(total_demand / effective_days, 3)

        # Current stock (take latest or max on-hand)
        if has_date:
            latest_idx = group["date"].idxmax()
            current_stock = float(group.loc[latest_idx, "current_stock"])
        else:
            current_stock = float(group["current_stock"].iloc[-1])

        unit_cost = float(group["unit_cost"].iloc[-1]) if "unit_cost" in group.columns else 0.0
        unit_price = float(group["unit_price"].iloc[-1]) if "unit_price" in group.columns else 0.0

        # Lead time and safety stock
        lead_time_val = group["lead_time_days"].iloc[-1] if "lead_time_days" in group.columns else None
        has_real_lead_time = lead_time_val is not None and not pd.isna(lead_time_val) and lead_time_val > 0
        lead_time = int(lead_time_val) if has_real_lead_time else DEFAULT_LEAD_TIME_DAYS

        safety_val = group["safety_stock"].iloc[-1] if "safety_stock" in group.columns else None
        has_real_safety = safety_val is not None and not pd.isna(safety_val)
        safety_stock = int(safety_val) if has_real_safety else int(round(avg_daily_demand * DEFAULT_SAFETY_STOCK_DAYS))

        rop_val = group["reorder_point"].iloc[-1] if "reorder_point" in group.columns else None
        has_real_rop = rop_val is not None and not pd.isna(rop_val)
        if has_real_rop:
            reorder_point = int(rop_val)
            rop_source = "Dataset Defined"
        else:
            reorder_point = int(round((avg_daily_demand * lead_time) + safety_stock))
            rop_source = "Estimated (Daily Demand × Lead Time + Safety Stock)"

        # Days of Inventory Remaining (Safe division)
        if avg_daily_demand > 0:
            days_of_inventory = round(current_stock / avg_daily_demand, 1)
        else:
            # 0 demand with stock means indefinite/dormant coverage
            days_of_inventory = 999.0 if current_stock > 0 else 0.0

        # Demand Velocity & Turnover
        # Consumption rate: percentage of stock sold per day
        demand_velocity = round(avg_daily_demand, 2)
        turnover_daily_pct = round((avg_daily_demand / current_stock * 100), 2) if current_stock > 0 else 0.0

        # Demand Trend calculation (Comparing first half vs second half of timeframe)
        demand_trend = "Stable"
        trend_pct = 0.0
        if has_date and len(group) >= 10:
            sorted_grp = group.sort_values("date")
            midpoint = len(sorted_grp) // 2
            first_half_avg = sorted_grp.iloc[:midpoint]["units_sold"].mean()
            second_half_avg = sorted_grp.iloc[midpoint:]["units_sold"].mean()
            
            if first_half_avg > 0:
                trend_pct = round(((second_half_avg - first_half_avg) / first_half_avg) * 100, 1)
                if trend_pct > 15.0:
                    demand_trend = "Increasing"
                elif trend_pct < -15.0:
                    demand_trend = "Decreasing"
                else:
                    demand_trend = "Stable"
            elif second_half_avg > 0:
                demand_trend = "Increasing"
                trend_pct = 100.0

        # Movement velocity classification
        if avg_daily_demand >= 4.0:
            movement_class = "Fast Moving"
        elif avg_daily_demand >= 1.0:
            movement_class = "Normal Moving"
        else:
            movement_class = "Slow Moving"

        # Overstock & Excess inventory calculations
        expected_demand_horizon = round(avg_daily_demand * overstock_days, 1)
        excess_inventory = max(0.0, round(current_stock - expected_demand_horizon, 1))
        excess_inventory_pct = round((excess_inventory / current_stock * 100), 1) if current_stock > 0 else 0.0
        overstock_value = round(excess_inventory * unit_cost, 2)
        total_inventory_value = round(current_stock * unit_cost, 2)

        # Inventory Status Engine (Explicit & Documented Hierarchy)
        # 1. Critical Stockout: Stock is zero OR coverage <= critical_days
        if current_stock <= 0 or (days_of_inventory <= critical_days and avg_daily_demand > 0):
            inventory_status = STATUS_CRITICAL
        # 2. Low Stock: Days of inventory <= low_stock_days OR stock <= reorder_point
        elif days_of_inventory <= low_stock_days or current_stock <= reorder_point:
            inventory_status = STATUS_LOW_STOCK
        # 3. Slow Moving: Low daily demand (< 1.0) and days of inventory > slow_moving_days
        elif movement_class == "Slow Moving" and days_of_inventory >= slow_moving_days:
            inventory_status = STATUS_SLOW_MOVING
        # 4. Overstock: Days of inventory > overstock_days
        elif days_of_inventory > overstock_days:
            inventory_status = STATUS_OVERSTOCK
        # 5. Healthy
        else:
            inventory_status = STATUS_HEALTHY

        # Last transaction date
        last_sale_date = group[group["units_sold"] > 0]["date"].max() if has_date else None
        last_sale_str = last_sale_date.strftime("%Y-%m-%d") if pd.notna(last_sale_date) else "N/A"

        product_records.append({
            "sku": sku,
            "product_name": prod_name,
            "category": cat,
            "current_stock": current_stock,
            "total_demand": total_demand,
            "avg_daily_demand": avg_daily_demand,
            "days_of_inventory": days_of_inventory,
            "lead_time_days": lead_time,
            "safety_stock": safety_stock,
            "reorder_point": reorder_point,
            "rop_source": rop_source,
            "unit_price": unit_price,
            "unit_cost": unit_cost,
            "inventory_value": total_inventory_value,
            "demand_velocity": demand_velocity,
            "turnover_daily_pct": turnover_daily_pct,
            "movement_class": movement_class,
            "demand_trend": demand_trend,
            "trend_pct": trend_pct,
            "expected_demand_horizon": expected_demand_horizon,
            "excess_inventory": excess_inventory,
            "excess_inventory_pct": excess_inventory_pct,
            "overstock_value": overstock_value,
            "inventory_status": inventory_status,
            "last_sale_date": last_sale_str
        })

    result_df = pd.DataFrame(product_records)
    return result_df

def compute_category_analytics(prod_analytics: pd.DataFrame) -> pd.DataFrame:
    """
    Computes category-level inventory summary, total demand, inventory valuation,
    and stock status distribution.
    """
    if prod_analytics.empty:
        return pd.DataFrame()

    cat_summary = prod_analytics.groupby("category").agg(
        total_products=("sku", "count"),
        total_inventory=("current_stock", "sum"),
        total_demand=("total_demand", "sum"),
        total_inventory_value=("inventory_value", "sum"),
        total_overstock_value=("overstock_value", "sum"),
        avg_days_of_inventory=("days_of_inventory", lambda s: round(s[s < 900].mean(), 1) if (s < 900).any() else 0.0),
        critical_count=("inventory_status", lambda s: (s == STATUS_CRITICAL).sum()),
        low_stock_count=("inventory_status", lambda s: (s == STATUS_LOW_STOCK).sum()),
        healthy_count=("inventory_status", lambda s: (s == STATUS_HEALTHY).sum()),
        overstock_count=("inventory_status", lambda s: (s == STATUS_OVERSTOCK).sum()),
        slow_moving_count=("inventory_status", lambda s: (s == STATUS_SLOW_MOVING).sum())
    ).reset_index()

    return cat_summary

def compute_time_series_demand(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    Computes aggregated demand over time at Daily ('D'), Weekly ('W'), or Monthly ('ME'/'M') intervals.
    """
    if df.empty or "date" not in df.columns:
        return pd.DataFrame()

    temp = df.copy()
    temp["date"] = pd.to_datetime(temp["date"])
    
    # Resample
    if freq == "W":
        resampled = temp.groupby([pd.Grouper(key="date", freq="W-MON"), "category"])["units_sold"].sum().reset_index()
    elif freq in ["M", "ME"]:
        resampled = temp.groupby([pd.Grouper(key="date", freq="ME"), "category"])["units_sold"].sum().reset_index()
    else:
        resampled = temp.groupby(["date", "category"])["units_sold"].sum().reset_index()

    return resampled
