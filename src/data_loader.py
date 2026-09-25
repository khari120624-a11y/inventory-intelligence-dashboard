"""
Data Loading and Flexible Column Mapping Module.
Automatically discovers and maps arbitrary column names to internal standardized analytics fields.
"""

import io
from typing import Dict, Any, Tuple, Optional
import pandas as pd

# Synonyms dictionary for flexible column discovery
COLUMN_SYNONYMS: Dict[str, list] = {
    "sku": [
        "sku", "product_id", "item_id", "product_code", "item_code", "id", "code", "part_number"
    ],
    "product_name": [
        "product_name", "product", "productname", "item", "item_name", "name", "title", "description"
    ],
    "category": [
        "category", "product_category", "department", "dept", "group", "product_group", "type", "class"
    ],
    "date": [
        "date", "order_date", "transaction_date", "sales_date", "datetime", "timestamp", "day", "time"
    ],
    "units_sold": [
        "units_sold", "quantity", "sales", "demand", "order_quantity", "qty", "volume", "units", "quantity_sold"
    ],
    "current_stock": [
        "current_stock", "stock", "inventory", "stock_level", "available_stock", "on_hand", "quantity_on_hand", "qty_on_hand"
    ],
    "unit_price": [
        "unit_price", "price", "selling_price", "retail_price", "unitprice", "sales_price"
    ],
    "unit_cost": [
        "unit_cost", "cost", "purchase_price", "cogs", "unitcost", "cost_price"
    ],
    "lead_time_days": [
        "lead_time_days", "lead_time", "leadtime", "supplier_lead_time", "delivery_days", "lead_days"
    ],
    "safety_stock": [
        "safety_stock", "safetystock", "buffer_stock", "min_stock", "minimum_stock"
    ],
    "reorder_point": [
        "reorder_point", "reorderpoint", "rop", "reorder_level"
    ]
}

def detect_column_mappings(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Examines input DataFrame columns and maps them to standard canonical names
    using normalized case-insensitive synonym matching.
    """
    mapping = {}
    df_cols_clean = {col: col.strip().lower().replace(" ", "_").replace("-", "_") for col in df.columns}
    
    assigned_cols = set()

    # Priority check for each canonical key
    for canonical_name, synonyms in COLUMN_SYNONYMS.items():
        found_col = None
        for syn in synonyms:
            for original_col, clean_col in df_cols_clean.items():
                if original_col in assigned_cols:
                    continue
                if clean_col == syn:
                    found_col = original_col
                    break
            if found_col:
                break
        
        # Partial containment check if exact match wasn't found
        if not found_col:
            for syn in synonyms:
                for original_col, clean_col in df_cols_clean.items():
                    if original_col in assigned_cols:
                        continue
                    if syn in clean_col and len(syn) > 2:
                        found_col = original_col
                        break
                if found_col:
                    break

        if found_col:
            mapping[canonical_name] = found_col
            assigned_cols.add(found_col)
        else:
            mapping[canonical_name] = None

    # Fallback: If sku was mapped but product_name wasn't, or vice-versa, use the available one
    if not mapping["product_name"] and mapping["sku"]:
        mapping["product_name"] = mapping["sku"]
    elif not mapping["sku"] and mapping["product_name"]:
        mapping["sku"] = mapping["product_name"]

    return mapping

def load_data_from_path(file_path: str) -> pd.DataFrame:
    """Loads CSV, Parquet, or Excel files into a pandas DataFrame."""
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith((".xls", ".xlsx")):
        return pd.read_excel(file_path)
    elif file_path.endswith(".parquet"):
        return pd.read_parquet(file_path)
    else:
        # Default try CSV
        return pd.read_csv(file_path)

def generate_data_profile(df: pd.DataFrame, file_name: str) -> Dict[str, Any]:
    """
    Computes a comprehensive data profile as required by Hackathon Step 1 & 2.
    """
    mapping = detect_column_mappings(df)
    
    # Missing required vs optional
    required_fields = ["product_name", "units_sold", "current_stock"]
    missing_required = [f for f in required_fields if mapping.get(f) is None]

    # Unique products
    prod_col = mapping.get("sku") or mapping.get("product_name")
    unique_products = df[prod_col].nunique() if prod_col and prod_col in df.columns else 0

    # Unique categories
    cat_col = mapping.get("category")
    unique_categories = df[cat_col].dropna().nunique() if cat_col and cat_col in df.columns else 1

    # Date range
    date_col = mapping.get("date")
    date_range_str = "No date column detected"
    if date_col and date_col in df.columns:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce").dropna()
        if not parsed_dates.empty:
            date_range_str = f"{parsed_dates.min().strftime('%Y-%m-%d')} to {parsed_dates.max().strftime('%Y-%m-%d')}"

    # Missing values dict
    missing_vals = df.isnull().sum().to_dict()

    profile = {
        "file_name": file_name,
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": missing_vals,
        "duplicate_count": int(df.duplicated().sum()),
        "date_range": date_range_str,
        "product_count": unique_products,
        "category_count": unique_categories,
        "demand_column": mapping.get("units_sold"),
        "inventory_column": mapping.get("current_stock"),
        "date_column": mapping.get("date"),
        "category_column": mapping.get("category"),
        "product_column": prod_col,
        "price_column": mapping.get("unit_price"),
        "cost_column": mapping.get("unit_cost"),
        "lead_time_column": mapping.get("lead_time_days"),
        "missing_required_fields": missing_required,
        "column_mapping": mapping
    }
    return profile
