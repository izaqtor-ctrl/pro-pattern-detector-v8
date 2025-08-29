# config.py
# Pattern Detector V8.0 - Configuration Settings

# Application Settings
APP_TITLE = "Pro Pattern Detector v8.0"
APP_SUBTITLE = "Modular Architecture - Professional Pattern Recognition"
VERSION = "8.0"

# Pattern Detection Settings
PATTERNS = ["Flat Top Breakout", "Bull Flag", "Cup Handle", "Inside Bar"]
DEFAULT_PATTERNS = ["Flat Top Breakout", "Bull Flag", "Inside Bar"]

# Timeframe Settings
PERIOD_OPTIONS = ["1mo", "3mo", "6mo", "1y", "1wk (Weekly)"]
DEFAULT_PERIOD = "3mo"

# Confidence Settings
MIN_CONFIDENCE_RANGE = (45, 85)
DEFAULT_MIN_CONFIDENCE = 55

# Volume Analysis Settings
VOLUME_THRESHOLDS = {
    "good": 1.3,
    "strong": 1.5,
    "exceptional": 2.0
}

VOLUME_SCORE_POINTS = {
    "exceptional": 25,  # 2.0x+ average
    "strong": 20,       # 1.5-2.0x average
    "good": 15,         # 1.3-1.5x average
    "weak": 0           # <1.3x average
}

# Pattern-specific volume bonuses
PATTERN_VOLUME_BONUS = {
    "Bull Flag": 20,      # Flagpole vs flag volume
    "Cup Handle": 20,     # Volume dryup in handle
    "Flat Top Breakout": 20,  # Breakout volume surge
    "Inside Bar": 15      # Consolidation volume
}

# Confidence Capping
MAX_CONFIDENCE_WITHOUT_VOLUME = 70

# Market Timing Settings
MARKET_TIMING_ADJUSTMENTS = {
    "weekend_penalty": 0.95,      # -5%
    "friday_penalty": 0.85,       # -15% without exceptional volume
    "midweek_bonus": 1.02,        # +2%
    "monday_gap_check": True
}

# Pattern Age Limits (days)
PATTERN_AGE_LIMITS = {
    "daily": {
        "Flat Top Breakout": 8,
        "Bull Flag": 10,
        "Cup Handle": 30,
        "Inside Bar": 6
    },
    "weekly": {
        "Flat Top Breakout": 8,  # weeks
        "Bull Flag": 10,         # weeks
        "Cup Handle": 30,        # weeks
        "Inside Bar": 8          # weeks
    }
}

# Risk Management Settings
RISK_MULTIPLIERS = {
    "volatility_stop": 1.5,  # 1.5x average daily range
    "min_stop_distance": {
        "Flat Top Breakout": 0.03,  # 3%
        "Bull Flag": 0.04,          # 4%
        "Cup Handle": 0.05,         # 5%
        "Inside Bar": 0.05          # 5%
    }
}

# Target Calculation Settings
MIN_RISK_REWARD_RATIOS = {
    "target1": 1.5,
    "target2": 2.5
}

# Inside Bar specific settings
INSIDE_BAR_CONFIG = {
    "entry_buffer": 1.05,    # 5% above inside bar high
    "stop_buffer": 0.95,     # 5% below inside bar low
    "target2_multiplier": 1.13,  # 13% above mother bar high
    "target3_multiplier": 1.21,  # 21% above mother bar high
    "max_inside_bars": 2,
    "preferred_inside_bars": 1
}

# Technical Indicator Settings
INDICATOR_PERIODS = {
    "rsi": 14,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "sma": 20,
    "volume_sma": 20
}

# Pattern Detection Thresholds
PATTERN_THRESHOLDS = {
    "Flat Top Breakout": {
        "min_initial_gain": 0.10,  # 10%
        "min_pullback": 0.08,      # 8%
        "resistance_tolerance": 0.98  # 98% of resistance level
    },
    "Bull Flag": {
        "min_flagpole_gain": 0.08,  # 8%
        "pullback_range": (-0.15, 0.05),  # -15% to +5%
        "flag_tolerance": 0.95
    },
    "Cup Handle": {
        "min_cup_depth": 0.08,     # 8%
        "max_cup_depth": 0.60,     # 60%
        "max_handle_depth": 0.25   # 25%
    },
    "Inside Bar": {
        "tight_consolidation": 0.30,    # 30% of mother bar (daily)
        "tight_consolidation_weekly": 0.35,  # 35% for weekly
        "good_consolidation": 0.50,
        "good_consolidation_weekly": 0.55,
        "moderate_consolidation": 0.70,
        "moderate_consolidation_weekly": 0.75
    }
}

# Chart Settings
CHART_CONFIG = {
    "height": 800,
    "volume_opacity": 0.7,
    "volume_colors": {
        "exceptional": "darkgreen",
        "strong": "green", 
        "good": "lightgreen",
        "weak": "red",
        "default": "blue"
    },
    "line_colors": {
        "entry": "green",
        "stop": "red",
        "target1": "lime",
        "target2": "darkgreen",
        "target3": "purple",
        "sma": "orange"
    }
}

# Demo Data Settings (when yfinance unavailable)
DEMO_DATA_CONFIG = {
    "base_price_range": (50, 250),
    "volatility": 0.02,
    "volume_range": (1000000, 5000000)
}

# Export Settings
EXPORT_FILENAME_FORMAT = "patterns_v8_{timestamp}.csv"

# Error Messages
ERROR_MESSAGES = {
    "insufficient_data": "Insufficient data for analysis",
    "no_patterns": "No patterns detected. Try lowering confidence threshold.",
    "yfinance_unavailable": "Using demo data (yfinance not available)",
    "data_fetch_error": "Error fetching data, using demo data"
}

# Warning Messages
WARNING_MESSAGES = {
    "demo_mode": "Demo Mode: Using simulated data",
    "weekend_analysis": "Weekend Analysis: Patterns based on Friday's close",
    "friday_risk": "Friday entries require exceptional volume for weekend holds",
    "monday_gap": "Monday gap risk - validate patterns post-open"
}

# Success Messages
SUCCESS_MESSAGES = {
    "pattern_detected": "Pattern detected with high confidence",
    "volume_confirmed": "Volume confirmation present",
    "optimal_timing": "Optimal timing for entry"
}

# Disclaimer
DISCLAIMER_TEXT = """
DISCLAIMER: Educational purposes only. Not financial advice. 
Trading involves substantial risk. Consult professionals before trading.
"""
