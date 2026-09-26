"""
Unit tests for data preprocessing pipeline.
"""

import pytest
import pandas as pd
import numpy as np

from src.preprocessing import preprocess_inventory_data

def test_preprocessing_deduplication_and_whitespace():
    raw_data = pd.DataFrame({
        "item_id": ["SKU-001", "SKU-001", "SKU-002"],
        "name": [" Widget A ", " Widget A ", "Widget B"],
        "category": [" electronics ", " electronics ", "HOME & KITCHEN"],
        "qty": [10, 10, -5],
        "stock": [100, 100, 20],
        "date": ["2026-01-01", "2026-01-01", "invalid-date"]
    })
    mapping = {
        "sku": "item_id",
        "product_name": "name",
        "category": "category",
        "units_sold": "qty",
        "current_stock": "stock",
        "date": "date",
        "unit_price": None,
        "unit_cost": None,
        "lead_time_days": None,
        "safety_stock": None,
        "reorder_point": None
    }

    clean_df, log = preprocess_inventory_data(raw_data, mapping)

    # Assert 1 duplicate row was removed
    assert len(clean_df) == 2
    assert log["duplicates_removed"] == 1

    # Assert whitespace trimmed and casing normalized
    assert clean_df["category"].iloc[0] == "Electronics"
    assert clean_df["category"].iloc[1] == "Home & Kitchen"

    # Assert negative quantity was clipped to 0
    assert clean_df["units_sold"].iloc[1] == 0.0
    assert log["negative_quantities_corrected"] == 1

    # Assert invalid date was handled without crashing
    assert pd.notna(clean_df["date"].iloc[1])
