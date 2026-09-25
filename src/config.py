"""
Configuration constants and thresholds for the Inventory Analytics Engine.
All thresholds are easily configurable and clearly documented.
"""

from typing import Dict

# Inventory Coverage Thresholds (in Days)
CRITICAL_STOCKOUT_DAYS: float = 3.0   # Stock remaining <= 3 days of demand
LOW_STOCK_DAYS: float = 7.0           # Stock remaining <= 7 days of demand
SLOW_MOVING_DAYS: float = 30.0        # Low velocity or > 30 days inventory with sluggish sales
OVERSTOCK_DAYS: float = 60.0          # Stock remaining > 60 days of demand

# Default operational parameters when not provided in raw dataset
DEFAULT_LEAD_TIME_DAYS: int = 14      # Assumed supplier lead time in days
DEFAULT_SAFETY_STOCK_DAYS: int = 5    # Assumed buffer safety stock in days

# Risk Scoring Weightings (Total = 1.0)
RISK_WEIGHTS: Dict[str, float] = {
    "coverage_urgency": 0.40,   # Days of inventory relative to lead time
    "stock_depletion": 0.25,    # Proximity of current stock to zero
    "demand_velocity": 0.20,    # Recent consumption velocity / demand momentum
    "lead_time_exposure": 0.15  # Supplier replenishment lag exposure
}

# Inventory Classification Statuses
STATUS_CRITICAL = "STOCK-OUT / CRITICAL"
STATUS_LOW_STOCK = "LOW STOCK"
STATUS_HEALTHY = "HEALTHY"
STATUS_OVERSTOCK = "OVERSTOCK"
STATUS_SLOW_MOVING = "SLOW-MOVING"

ALL_STATUSES = [
    STATUS_CRITICAL,
    STATUS_LOW_STOCK,
    STATUS_HEALTHY,
    STATUS_OVERSTOCK,
    STATUS_SLOW_MOVING
]

# Risk Level Tiers
RISK_TIER_LOW = "Low Risk"         # 0 - 30
RISK_TIER_MEDIUM = "Medium Risk"   # 31 - 60
RISK_TIER_HIGH = "High Risk"       # 61 - 80
RISK_TIER_CRITICAL = "Critical"    # 81 - 100

# Color Mapping for Consistent UI / Plotly Themes
STATUS_COLORS: Dict[str, str] = {
    STATUS_CRITICAL: "#EF4444",    # Vibrant Red
    STATUS_LOW_STOCK: "#F59E0B",   # Amber / Orange
    STATUS_HEALTHY: "#10B981",     # Emerald Green
    STATUS_OVERSTOCK: "#6366F1",   # Indigo Blue
    STATUS_SLOW_MOVING: "#8B5CF6"  # Purple
}

RISK_TIER_COLORS: Dict[str, str] = {
    RISK_TIER_LOW: "#10B981",
    RISK_TIER_MEDIUM: "#3B82F6",
    RISK_TIER_HIGH: "#F59E0B",
    RISK_TIER_CRITICAL: "#EF4444"
}
