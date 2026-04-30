"""Constants and configuration for Zolve MVP."""

# Coin earning weights (from spec)
EARNING_WEIGHTS = {
    "on_time_payment": 500,
    "credit_score_up": 400,
    "savings_milestone": 350,
    "direct_deposit": 200,
    "education_module": 150,
    "daily_checkin": 50,
    "ad_watch": 10,
    "referral": 300,
    "easter_egg": 200,
}

# Tier thresholds
TIER_THRESHOLDS = {
    "Basic": {"min_coins": 0, "min_behaviors": 0},
    "Silver": {"min_coins": 1000, "min_behaviors": 2},
    "Gold": {"min_coins": 3000, "min_behaviors": 5},
}

# Daily earning caps (anti-abuse)
DAILY_EARNING_CAPS = {
    "daily_checkin": 50,  # Can only claim once per day
    "ad_watch": 30,  # Max 3 ads per day @ 10 coins each
    "education_module": 150,  # Max 1 per day
}

# Game mechanics
SCRATCH_CARD_PROBABILITIES = {
    "try_again": 0.40,
    "small_win": 0.35,
    "medium_win": 0.20,
    "jackpot": 0.05,
}

SCRATCH_CARD_REWARDS = {
    "try_again": 0,
    "small_win": 50,
    "medium_win": 150,
    "jackpot": 500,
}

SPIN_WHEEL_COST = 100
SPIN_WHEEL_REWARDS = [50, 100, 200, 300, 500, 1000]

# Z-Kart pricing
ZMART_COIN_DISCOUNT_RANGE = (5, 10)  # 5-10% additional discount with coins
MINIMUM_PRODUCT_PRICE = 100.0
MAXIMUM_PRODUCT_PRICE = 5000.0

# Flash deals
FLASH_DEAL_DURATION_MINUTES = 60
FLASH_DEAL_TIER_REQUIREMENTS = {
    "flash_bronze": "Basic",
    "flash_silver": "Silver",
    "flash_gold": "Gold",
}

# Behavior verification
VERIFICATION_METHODS = ["bank_api", "credit_bureau", "user_self_report"]
BEHAVIOR_TYPES = [
    "on_time_payment",
    "credit_score_up",
    "savings_milestone",
    "direct_deposit",
    "daily_checkin",
    "education_module",
    "ad_watch",
    "referral",
    "easter_egg",
]

# Mock bank data (for demo)
MOCK_BANKS = ["HDFC", "ICICI", "Axis"]

# Credit score ranges
MIN_CREDIT_SCORE = 300
MAX_CREDIT_SCORE = 900
DEFAULT_CREDIT_SCORE = 650

# Demo user
DEMO_USER_ID = 1
DEMO_USER_NAME = "Demo User"
DEMO_USER_EMAIL = "demo@zolve.app"

# Database
DATABASE_PATH = "zolve.db"

# API
API_HOST = "localhost"
API_PORT = 8000
API_RELOAD = True
