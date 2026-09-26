"""
Unit tests for Inventory Risk Scoring Engine.
"""

import pytest
import pandas as pd
from src.risk_engine import compute_inventory_risk_score, attach_risk_scores
from src.config import RISK_TIER_CRITICAL, RISK_TIER_LOW

def test_inventory_risk_score_bounds_and_transparency():
    # Test case 1: Stockout item
    stockout_item = pd.Series({
        "current_stock": 0.0,
        "avg_daily_demand": 10.0,
        "days_of_inventory": 0.0,
        "lead_time_days": 14,
        "demand_trend": "Increasing",
        "trend_pct": 25.0
    })
    score, tier, breakdown = compute_inventory_risk_score(stockout_item)
    assert score == 100
    assert tier == RISK_TIER_CRITICAL
    assert "coverage_penalty" in breakdown
    assert "stock_depletion_penalty" in breakdown

    # Test case 2: Abundantly stocked item
    safe_item = pd.Series({
        "current_stock": 500.0,
        "avg_daily_demand": 2.0,
        "days_of_inventory": 250.0,
        "lead_time_days": 7,
        "demand_trend": "Stable",
        "trend_pct": 0.0
    })
    score2, tier2, breakdown2 = compute_inventory_risk_score(safe_item)
    assert 0 <= score2 <= 30
    assert tier2 == RISK_TIER_LOW

    # Ensure all scores stay strictly in [0, 100]
    df = pd.DataFrame([stockout_item, safe_item])
    df_scored = attach_risk_scores(df)
    assert df_scored["inventory_risk_score"].min() >= 0
    assert df_scored["inventory_risk_score"].max() <= 100
