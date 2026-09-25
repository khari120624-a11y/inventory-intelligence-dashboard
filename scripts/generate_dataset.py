"""
Benchmark Data Generator for Inventory Analytics Hackathon
Generates realistic retail inventory and transactional demand data with deliberate real-world messiness
(duplicates, whitespace, mixed casing, occasional nulls) to validate preprocessing, analytics, and ML forecasting.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_inventory_data():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("exports", exist_ok=True)
    
    random.seed(42)
    np.random.seed(42)

    categories = {
        "Electronics": [
            ("SKU-ELC-001", "Wireless Noise-Canceling Headphones", 129.99, 65.00, 12, 14, "high_demand_stockout_risk"),
            ("SKU-ELC-002", "Smart Fitness Watch V2", 189.50, 95.00, 48, 10, "healthy"),
            ("SKU-ELC-003", "4K Ultra-HD Action Camera", 249.00, 130.00, 420, 21, "overstock"),
            ("SKU-ELC-004", "USB-C Fast Charging Cable 2M", 14.99, 3.20, 5, 7, "critical_stockout"),
            ("SKU-ELC-005", "Vintage Stereo Turntable", 319.00, 180.00, 85, 28, "slow_moving"),
            ("SKU-ELC-006", "Bluetooth Conference Speaker", 89.99, 42.00, 65, 14, "healthy"),
            ("SKU-ELC-007", "Ergonomic Mechanical Keyboard", 119.00, 58.00, 18, 12, "low_stock"),
        ],
        "Home & Kitchen": [
            ("SKU-HMK-101", "Digital Air Fryer Oven 6Qt", 99.99, 48.00, 14, 14, "high_demand_stockout_risk"),
            ("SKU-HMK-102", "Stainless Steel French Press", 34.50, 14.00, 110, 10, "healthy"),
            ("SKU-HMK-103", "Cold Brew Iced Coffee Pitcher", 27.99, 11.50, 390, 15, "overstock"),
            ("SKU-HMK-104", "Electric Precision Milk Frother", 19.99, 6.50, 0, 7, "critical_stockout"),
            ("SKU-HMK-105", "Cast Iron Dutch Oven 5.5Qt", 84.99, 41.00, 140, 21, "slow_moving"),
            ("SKU-HMK-106", "Smart WiFi Food Scale", 39.99, 17.50, 92, 12, "healthy"),
            ("SKU-HMK-107", "Silicone Baking Mat Set", 18.50, 6.00, 22, 10, "low_stock"),
        ],
        "Apparel": [
            ("SKU-APP-201", "Thermal Fleece Running Hoodie", 59.99, 24.00, 16, 14, "high_demand_stockout_risk"),
            ("SKU-APP-202", "Moisture-Wicking Athletic Tee", 28.00, 9.50, 220, 10, "healthy"),
            ("SKU-APP-203", "Heavyweight Arctic Winter Parka", 179.99, 85.00, 510, 30, "overstock"),
            ("SKU-APP-204", "Seamless Workout Compression Leggings", 44.99, 16.00, 4, 10, "critical_stockout"),
            ("SKU-APP-205", "Formal Wool Blazer Tailored", 219.00, 110.00, 115, 25, "slow_moving"),
            ("SKU-APP-206", "Organic Cotton Crewneck Sweatshirt", 49.50, 20.00, 135, 12, "healthy"),
        ],
        "Health & Personal Care": [
            ("SKU-HPC-301", "Sonic Electric Toothbrush Pro", 69.99, 29.00, 25, 14, "low_stock"),
            ("SKU-HPC-302", "Collagen Peptide Powder 500g", 36.00, 15.00, 160, 12, "healthy"),
            ("SKU-HPC-303", "Infrared Shiatsu Neck Massager", 54.99, 22.00, 340, 20, "overstock"),
            ("SKU-HPC-304", "Daily Multivitamin Gummies 120ct", 22.50, 8.50, 8, 7, "critical_stockout"),
            ("SKU-HPC-305", "Aromatherapy Ultrasonic Diffuser", 32.99, 13.50, 180, 18, "slow_moving"),
        ],
        "Sports & Outdoors": [
            ("SKU-SPO-401", "Insulated Hydro Water Bottle 32oz", 29.99, 11.00, 20, 10, "low_stock"),
            ("SKU-SPO-402", "Non-Slip High Density Yoga Mat", 38.00, 16.00, 150, 14, "healthy"),
            ("SKU-SPO-403", "Heavy-Duty Resistance Bands Set", 24.99, 8.00, 480, 15, "overstock"),
            ("SKU-SPO-404", "Ultralight Backpacking Tent 2-Person", 199.99, 98.00, 75, 28, "slow_moving"),
            ("SKU-SPO-405", "Compact Camping Hammock Portable", 34.99, 13.00, 95, 14, "healthy"),
        ]
    }

    start_date = datetime(2026, 3, 1)
    num_days = 180
    dates = [start_date + timedelta(days=i) for i in range(num_days)]

    records = []
    
    for category, products in categories.items():
        for sku, name, price, cost, stock, lead_time, profile in products:
            # Base daily demand based on profile
            if profile == "high_demand_stockout_risk":
                base_demand = 8.5
            elif profile == "critical_stockout":
                base_demand = 7.0
            elif profile == "low_stock":
                base_demand = 5.2
            elif profile == "healthy":
                base_demand = 4.0
            elif profile == "overstock":
                base_demand = 1.8
            elif profile == "slow_moving":
                base_demand = 0.4
            else:
                base_demand = 3.0

            safety_stock = int(round(base_demand * (lead_time * 0.4)))
            reorder_point = int(round((base_demand * lead_time) + safety_stock))

            for dt in dates:
                # Add weekend surge (Saturday/Sunday)
                is_weekend = dt.weekday() >= 5
                weekend_mult = 1.35 if is_weekend else 1.0

                # Slight positive or negative trend
                day_idx = (dt - start_date).days
                if profile in ["high_demand_stockout_risk", "critical_stockout"]:
                    trend_mult = 1.0 + (day_idx / num_days) * 0.4
                elif profile in ["slow_moving", "overstock"]:
                    trend_mult = 1.0 - (day_idx / num_days) * 0.25
                else:
                    trend_mult = 1.0 + (np.sin(day_idx / 15.0) * 0.15)

                mean_d = base_demand * weekend_mult * trend_mult
                
                # Zero sales days for slow moving
                if profile == "slow_moving" and random.random() < 0.65:
                    units_sold = 0
                else:
                    units_sold = max(0, int(np.random.poisson(max(0.1, mean_d))))

                # Only emit transactions if sales occur or simulate regular store sales
                # To keep realistic transaction logs:
                records.append({
                    "Date": dt.strftime("%Y-%m-%d"),
                    "SKU": sku,
                    "Product_Name": name,
                    "Category": category,
                    "Units_Sold": units_sold,
                    "Unit_Price": price,
                    "Unit_Cost": cost,
                    "Current_Stock": stock,
                    "Lead_Time_Days": lead_time,
                    "Safety_Stock": safety_stock,
                    "Reorder_Point": reorder_point
                })

    df = pd.DataFrame(records)

    # Inject realistic real-world noise for preprocessing validation:
    # 1. Trailing / leading whitespace in some category names and product names
    df.loc[df["Category"] == "Electronics", "Category"] = df.loc[df["Category"] == "Electronics", "Category"].apply(
        lambda x: "  Electronics " if random.random() < 0.1 else x
    )
    # 2. Inconsistent category casing
    df.loc[df["Category"] == "Home & Kitchen", "Category"] = df.loc[df["Category"] == "Home & Kitchen", "Category"].apply(
        lambda x: "home & kitchen" if random.random() < 0.08 else x
    )
    # 3. Add duplicate rows (e.g. 15 duplicate rows)
    dup_rows = df.sample(n=15, random_state=42)
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 4. Introduce 3 anomalous negative sales (e.g. returns entered incorrectly as negative)
    neg_indices = df.sample(n=3, random_state=99).index
    df.loc[neg_indices, "Units_Sold"] = -1

    # 5. Introduce a few missing values in optional fields (e.g. Unit_Price)
    null_indices = df.sample(n=5, random_state=123).index
    df.loc[null_indices, "Unit_Price"] = np.nan

    output_path = "data/raw/retail_inventory_transactions.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} records saved to {output_path}")

if __name__ == "__main__":
    generate_inventory_data()
