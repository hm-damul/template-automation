"""System configuration management"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GUMROAD_API_KEY = os.getenv("GUMROAD_API_KEY")
    LEMON_SQUEEZY_API_KEY = os.getenv("LEMON_SQUEEZY_API_KEY")
    ETSY_API_KEY = os.getenv("ETSY_API_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")

    @classmethod
    def validate(cls):
        required = [cls.OPENAI_API_KEY, cls.GUMROAD_API_KEY, cls.SUPABASE_URL]
        return all(required)


class PlatformLimits:
    GUMROAD = {"daily_max": 10, "new_account_daily_max": 5}
    ETSY = {"daily_max": 5, "new_account_daily_max": 2}
    LEMON_SQUEEZY = {"daily_max": 10}

    @classmethod
    def get_random_daily_count(cls, platform):
        import random
        limits = getattr(cls, platform.upper(), {"daily_max": 3})
        base_max = limits.get("daily_max", 3)
        return random.randint(max(1, int(base_max * 0.3)), base_max)


class PricingStrategy:
    LOW_TIER = (8, 19)
    MID_TIER = (40, 80)
    HIGH_TIER = (100, 250)
    BUNDLE_DISCOUNT_MIN = 0.30
    BUNDLE_DISCOUNT_MAX = 0.60
    SEASONAL_DISCOUNT = 0.50


class RiskThresholds:
    DUPLICATE_SIMILARITY_THRESHOLD = 5
    AI_GENERATION_THRESHOLD = 0.30
    SALES_DROP_THRESHOLD = 0.50


config = Config()
