"""
Unit tests for inventory analytics and stock classification engine.
"""

import pytest
import pandas as pd
from src.analytics import compute_product_analytics
from src.config import (
    STATUS_CRITICAL,
    STATUS_LOW_STOCK,
    STATUS_HEALTHY,
    STATUS_OVERSTOCK,
    STATUS_SLOW_MOVING
)

def test_inventory_analytics_and_classification():
    # 5 test products modeling each status
    sample_df = pd.DataFrame([
        # Product 1: 0 stock -> Critical stockout
        {"sku": "P1", "product_name": "Zero Stock Item", "category": "Tech", "date": pd.Timestamp("2026-01-01"), "units_sold": 5.0, "current_stock": 0.0, "unit_price": 10.0, "unit_cost": 5.0, "lead_time_days": 10},
        # Product 2: Low stock -> 10 stock, 5/day demand = 2 days coverage (critical/low)
        {"sku": "P2", "product_name": "Low Stock Item", "category": "Tech", "date": pd.Timestamp("2026-01-01"), "units_sold": 5.0, "current_stock": 10.0, "unit_price": 10.0, "unit_cost": 5.0, "lead_time_days": 10},
        # Product 3: Healthy -> 100 stock, 5/day demand = 20 days coverage
        {"sku": "P3", "product_name": "Healthy Item", "category": "Tech", "date": pd.Timestamp("2026-01-01"), "units_sold": 5.0, "current_stock": 100.0, "unit_price": 10.0, "unit_cost": 5.0, "lead_time_days": 10},
        # Product 4: Overstock -> 500 stock, 5/day demand = 100 days coverage (> 60 days)
        {"sku": "P4", "product_name": "Overstock Item", "category": "Tech", "date": pd.Timestamp("2026-01-01"), "units_sold": 5.0, "current_stock": 500.0, "unit_price": 10.0, "unit_cost": 5.0, "lead_time_days": 10},
        # Product 5: Slow Moving -> 200 stock, 0.2/day demand = 1000 days coverage (< 1.0 demand velocity)
        {"sku": "P5", "product_name": "Slow Item", "category": "Tech", "date": pd.Timestamp("2026-01-01"), "units_sold": 0.2, "current_stock": 200.0, "unit_price": 10.0, "unit_cost": 5.0, "lead_time_days": 10},
    ])

    results = compute_product_analytics(sample_df)

    p1 = results[results["sku"] == "P1"].iloc[0]
    assert p1["inventory_status"] == STATUS_CRITICAL
    assert p1["days_of_inventory"] == 0.0

    p2 = results[results["sku"] == "P2"].iloc[0]
    assert p2["inventory_status"] == STATUS_CRITICAL  # 2 days <= 3 days critical threshold

    p3 = results[results["sku"] == "P3"].iloc[0]
    assert p3["inventory_status"] == STATUS_HEALTHY
    assert p3["days_of_inventory"] == 20.0

    p4 = results[results["sku"] == "P4"].iloc[0]
    assert p4["inventory_status"] == STATUS_OVERSTOCK
    assert p4["excess_inventory"] > 0

    p5 = results[results["sku"] == "P5"].iloc[0]
    assert p5["inventory_status"] == STATUS_SLOW_MOVING
    assert p5["movement_class"] == "Slow Moving"

def test_safe_division_zero_demand():
    sample_zero_demand = pd.DataFrame([
        {"sku": "P0", "product_name": "Zero Demand Item", "category": "Tech", "date": pd.Timestamp("2026-01-01"), "units_sold": 0.0, "current_stock": 50.0, "unit_price": 10.0, "unit_cost": 5.0, "lead_time_days": 10},
    ])
    results = compute_product_analytics(sample_zero_demand)
    p0 = results.iloc[0]
    # Zero demand must not throw ZeroDivisionError; days of inventory handles safely
    assert p0["avg_daily_demand"] == 0.0
    assert p0["days_of_inventory"] == 999.0
