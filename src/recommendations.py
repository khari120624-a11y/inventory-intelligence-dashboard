"""
Explainable Recommendation Engine.
Produces actionable procurement and inventory optimization decisions accompanied by transparent,
data-backed explanations and quantified operational impacts.
"""

from typing import Dict, Any, Tuple
import pandas as pd

from src.config import (
    STATUS_CRITICAL,
    STATUS_LOW_STOCK,
    STATUS_HEALTHY,
    STATUS_OVERSTOCK,
    STATUS_SLOW_MOVING
)

def generate_product_recommendation(row: pd.Series) -> Tuple[str, str, str, str]:
    """
    Evaluates product metrics and generates:
    (primary_action, rationale, operational_impact, action_badge_color)
    """
    status = str(row.get("inventory_status", STATUS_HEALTHY))
    current_stock = float(row.get("current_stock", 0))
    avg_demand = float(row.get("avg_daily_demand", 0))
    days_inv = float(row.get("days_of_inventory", 0))
    lead_time = int(row.get("lead_time_days", 14))
    reorder_point = int(row.get("reorder_point", 0))
    excess_qty = float(row.get("excess_inventory", 0))
    overstock_val = float(row.get("overstock_value", 0))
    trend = str(row.get("demand_trend", "Stable"))
    trend_pct = float(row.get("trend_pct", 0.0))

    if status == STATUS_CRITICAL:
        if current_stock <= 0:
            action = "Prioritize Urgent Replenishment (Emergency Expedite)"
            rationale = (
                f"Product is currently completely stocked out (0 units on hand) while daily demand "
                f"averages {avg_demand:.1f} units/day. Expedited supplier delivery required to mitigate recurring revenue loss."
            )
            impact = "Immediate lost revenue risk; customer fulfillment stalled."
            badge_color = "#EF4444"
        else:
            action = "Prioritize Immediate Replenishment"
            rationale = (
                f"Critical stock-out risk: Current inventory of {int(current_stock)} units covers only {days_inv:.1f} days "
                f"of demand, far below supplier lead time of {lead_time} days."
            )
            impact = f"Stock exhaustion projected within {days_inv:.1f} days if not replenished."
            badge_color = "#EF4444"

    elif status == STATUS_LOW_STOCK:
        action = "Initiate Standard Purchase Reorder"
        rationale = (
            f"Current inventory ({int(current_stock)} units) has breached the reorder threshold of {reorder_point} units "
            f"with {days_inv:.1f} days of inventory remaining. Reorder now to maintain minimum safety buffer."
        )
        impact = f"Supplier replenishment cycle takes {lead_time} days. Reordering now avoids stockout."
        badge_color = "#F59E0B"

    elif status == STATUS_OVERSTOCK:
        action = "Halt Replenishment & Stimulate Demand"
        rationale = (
            f"Excess inventory of {int(excess_qty)} units detected ({days_inv:.0f} days of coverage), exceeding the "
            f"60-day operational target. Working capital tied up equals ${overstock_val:,.2f}."
        )
        impact = f"Frees approximately ${overstock_val:,.2f} in working capital by pausing purchasing and bundling."
        badge_color = "#6366F1"

    elif status == STATUS_SLOW_MOVING:
        action = "Review Purchasing Levels & Evaluate Promotional Repositioning"
        rationale = (
            f"Sluggish sales velocity ({avg_demand:.2f} units/day) with {days_inv:.0f} days of inventory remaining. "
            f"Demand momentum is {trend.lower()} ({trend_pct:+.1f}% shift). Re-evaluate purchase orders and consider markdown tests."
        )
        impact = "Reduces warehouse carrying overhead and prevents terminal product obsolescence."
        badge_color = "#8B5CF6"

    else:  # STATUS_HEALTHY
        action = "Maintain Scheduled Monitoring"
        rationale = (
            f"Inventory levels ({int(current_stock)} units, {days_inv:.1f} days coverage) are balanced with current daily consumption "
            f"of {avg_demand:.1f} units/day and lead time of {lead_time} days."
        )
        impact = "Supply and demand equilibrium maintained with optimal safety buffer."
        badge_color = "#10B981"

    return action, rationale, impact, badge_color

def attach_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enriches analytics dataframe with data-driven recommendations and explanations.
    """
    if df.empty:
        return df

    actions = []
    rationales = []
    impacts = []
    colors = []

    for _, row in df.iterrows():
        action, rationale, impact, badge_color = generate_product_recommendation(row)
        actions.append(action)
        rationales.append(rationale)
        impacts.append(impact)
        colors.append(badge_color)

    df["recommended_action"] = actions
    df["recommendation_rationale"] = rationales
    df["expected_impact"] = impacts
    df["action_color"] = colors

    return df
