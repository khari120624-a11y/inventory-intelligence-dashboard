import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import load_data_from_path, generate_data_profile, detect_column_mappings
from src.preprocessing import preprocess_inventory_data, save_processed_data
from src.analytics import compute_product_analytics, compute_category_analytics, compute_time_series_demand
from src.risk_engine import attach_risk_scores
from src.recommendations import attach_recommendations
from src.forecasting import forecast_product_demand
from src.export_engine import generate_powerbi_exports

def run_verification():
    raw_path = "data/raw/retail_inventory_transactions.csv"
    print(f"Loading {raw_path}...")
    raw_df = load_data_from_path(raw_path)
    
    # 1. Profile
    profile = generate_data_profile(raw_df, "retail_inventory_transactions.csv")
    print("--- DATA PROFILE ---")
    print(f"File: {profile['file_name']}")
    print(f"Rows: {profile['rows']}, Cols: {profile['columns']}")
    print(f"Date Range: {profile['date_range']}")
    print(f"Products: {profile['product_count']}, Categories: {profile['category_count']}")
    print(f"Missing required fields: {profile['missing_required_fields']}")
    
    # 2. Preprocess
    mapping = profile["column_mapping"]
    clean_df, audit_log = preprocess_inventory_data(raw_df, mapping)
    save_processed_data(clean_df, "data/processed/retail_inventory_cleaned.csv")
    print("--- PREPROCESSING AUDIT ---")
    print(f"Duplicates removed: {audit_log['duplicates_removed']}")
    print(f"Negative quantities corrected: {audit_log['negative_quantities_corrected']}")
    print(f"Rows after cleaning: {audit_log['rows_after_cleaning']}")
    for d in audit_log["cleaning_decisions"]:
        print(f"  * {d}")

    # 3. Analytics
    prod_analytics = compute_product_analytics(clean_df)
    cat_summary = compute_category_analytics(prod_analytics)
    print("--- ANALYTICS ---")
    print(f"Analyzed {len(prod_analytics)} products across {len(cat_summary)} categories.")
    print("Inventory Status Distribution:")
    print(prod_analytics["inventory_status"].value_counts())

    # 4. Risk Engine
    prod_analytics = attach_risk_scores(prod_analytics)
    print("Risk Tier Distribution:")
    print(prod_analytics["risk_tier"].value_counts())

    # 5. Recommendations
    prod_analytics = attach_recommendations(prod_analytics)
    print("Sample Recommendations:")
    for _, row in prod_analytics.head(3).iterrows():
        print(f"[{row['inventory_status']}] {row['product_name']}: {row['recommended_action']}")
        print(f"  Rationale: {row['recommendation_rationale']}")

    # 6. Forecasting
    sample_sku = prod_analytics["sku"].iloc[0]
    sample_df = clean_df[clean_df["sku"] == sample_sku]
    fc = forecast_product_demand(sample_df, horizon_days=14)
    print("--- FORECASTING TEST ---")
    print(f"Forecast for {sample_sku}: {fc['message']}")
    if fc["success"]:
        print(f"MAE: {fc['metrics']['MAE']}, RMSE: {fc['metrics']['RMSE']}")

    # 7. Power BI Exports
    exports = generate_powerbi_exports(prod_analytics, clean_df, cat_summary, "exports")
    print("--- POWER BI EXPORTS ---")
    for name, path in exports.items():
        print(f"  Generated: {path}")

    print("\nVerification pipeline PASSED successfully!")

if __name__ == "__main__":
    run_verification()
