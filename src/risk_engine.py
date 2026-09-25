"""
Inventory Risk Scoring Engine.
Calculates a multi-factor 'Inventory Risk Score' (0-100) reflecting stock-out vulnerability,
replenishment lag, and consumption acceleration with full transparency.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.config import (
    RISK_TIER_LOW,
    RISK_TIER_MEDIUM,
    RISK_TIER_HIGH,
    RISK_TIER_CRITICAL,
    DEFAULT_LEAD_TIME_DAYS
)

def compute_inventory_risk_score(row: pd.Series) -> Tuple[int, str, Dict[str, float]]:
    """
    Computes transparent multi-factor Inventory Risk Score (0-100) for a single product.
    Returns:
        (risk_score, risk_tier, score_breakdown)
    """
    current_stock = float(row.get("current_stock", 0))
    avg_demand = float(row.get("avg_daily_demand", 0))
    days_inv = float(row.get("days_of_inventory", 0))
    lead_time = float(row.get("lead_time_days", DEFAULT_LEAD_TIME_DAYS))
    safety_stock = float(row.get("safety_stock", 0))
    reorder_point = float(row.get("reorder_point", 0))
    trend = str(row.get("demand_trend", "Stable"))
    trend_pct = float(row.get("trend_pct", 0.0))

    # Immediate absolute critical condition
    if current_stock <= 0:
        return 100, RISK_TIER_CRITICAL, {
            "coverage_penalty": 40.0,
            "stock_depletion_penalty": 25.0,
            "demand_trend_penalty": 20.0 if avg_demand > 0 else 5.0,
            "lead_time_exposure": 15.0
        }

    # Factor 1: Coverage Urgency (0 to 40 Points)
    # How soon will stock run out relative to lead time?
    # If days_inv < lead_time, goods cannot arrive before stockout!
    if days_inv <= 0:
        cov_pts = 40.0
    elif days_inv <= 3.0:
        cov_pts = 40.0
    elif days_inv < lead_time:
        # Stock runs out before normal shipment arrives
        ratio = (lead_time - days_inv) / lead_time
        cov_pts = 28.0 + (ratio * 12.0)
    elif days_inv <= (lead_time + 7.0):
        # Within safe cushion window
        cov_pts = 16.0
    elif days_inv <= 30.0:
        cov_pts = 6.0
    else:
        # Plenty of coverage
        cov_pts = 0.0

    # Factor 2: Stock Depletion & Reorder Proximity (0 to 25 Points)
    if current_stock <= 0:
        dep_pts = 25.0
    elif days_inv <= 3.0 and avg_demand > 0:
        # Imminent stock exhaustion (within 3 days) — maximum depletion urgency
        dep_pts = 25.0
    elif reorder_point > 0 and current_stock <= (reorder_point * 0.5):
        dep_pts = 22.0
    elif reorder_point > 0 and current_stock <= reorder_point:
        dep_pts = 15.0
    elif current_stock < 15:
        dep_pts = 10.0
    else:
        dep_pts = 2.0

    # Factor 3: Demand Trend & Velocity (0 to 20 Points)
    # Accelerating demand on limited stock increases stockout risk dramatically
    if trend == "Increasing" and days_inv < 21.0:
        trend_pts = min(20.0, 10.0 + abs(trend_pct) * 0.15)
    elif avg_demand >= 5.0 and days_inv < 14.0:
        trend_pts = 14.0
    elif trend == "Increasing":
        trend_pts = 8.0
    elif trend == "Stable" and days_inv < 10.0:
        trend_pts = 6.0
    else:
        trend_pts = 0.0

    # Factor 4: Supplier Lead Time Exposure (0 to 15 Points)
    # Longer supplier lead time means longer vulnerability window if reorder is delayed
    if lead_time >= 21:
        lead_pts = 15.0
    elif lead_time >= 14:
        lead_pts = 10.0
    elif lead_time >= 7:
        lead_pts = 5.0
    else:
        lead_pts = 2.0

    total_score = int(round(cov_pts + dep_pts + trend_pts + lead_pts))
    total_score = max(0, min(100, total_score))

    # Determine Risk Tier
    if total_score >= 81:
        risk_tier = RISK_TIER_CRITICAL
    elif total_score >= 61:
        risk_tier = RISK_TIER_HIGH
    elif total_score >= 31:
        risk_tier = RISK_TIER_MEDIUM
    else:
        risk_tier = RISK_TIER_LOW

    breakdown = {
        "coverage_penalty": round(cov_pts, 1),
        "stock_depletion_penalty": round(dep_pts, 1),
        "demand_trend_penalty": round(trend_pts, 1),
        "lead_time_exposure": round(lead_pts, 1)
    }

    return total_score, risk_tier, breakdown

def attach_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies inventory risk scoring to all products in analytics dataframe.
    """
    if df.empty:
        return df

    scores = []
    tiers = []
    cov_penalties = []
    dep_penalties = []
    trend_penalties = []
    lead_penalties = []

    for _, row in df.iterrows():
        score, tier, bdown = compute_inventory_risk_score(row)
        scores.append(score)
        tiers.append(tier)
        cov_penalties.append(bdown["coverage_penalty"])
        dep_penalties.append(bdown["stock_depletion_penalty"])
        trend_penalties.append(bdown["demand_trend_penalty"])
        lead_penalties.append(bdown["lead_time_exposure"])

    df["inventory_risk_score"] = scores
    df["risk_tier"] = tiers
    df["risk_coverage_score"] = cov_penalties
    df["risk_depletion_score"] = dep_penalties
    df["risk_trend_score"] = trend_penalties
    df["risk_lead_time_score"] = lead_penalties

    return df
