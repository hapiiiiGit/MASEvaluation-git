import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    # Facebook OAuth
    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")
    FACEBOOK_REDIRECT_URI = os.getenv("FACEBOOK_REDIRECT_URI", "http://localhost:8000/auth/facebook/callback")
    FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN")
    FACEBOOK_AD_ACCOUNT_ID = os.getenv("FACEBOOK_AD_ACCOUNT_ID")

    # HubSpot OAuth
    HUBSPOT_CLIENT_ID = os.getenv("HUBSPOT_CLIENT_ID")
    HUBSPOT_CLIENT_SECRET = os.getenv("HUBSPOT_CLIENT_SECRET")
    HUBSPOT_REDIRECT_URI = os.getenv("HUBSPOT_REDIRECT_URI", "http://localhost:8000/auth/hubspot/callback")
    HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")

    # Sync routine
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", 3600))  # Default: 1 hour

    # Notification settings
    NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL")
    NOTIFY_SLACK_WEBHOOK = os.getenv("NOTIFY_SLACK_WEBHOOK")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Database (if used in future)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Other settings
    ENV = os.getenv("ENV", "development")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.FACEBOOK_CLIENT_ID:
            missing.append("FACEBOOK_CLIENT_ID")
        if not cls.FACEBOOK_CLIENT_SECRET:
            missing.append("FACEBOOK_CLIENT_SECRET")
        if not cls.FACEBOOK_AD_ACCOUNT_ID:
            missing.append("FACEBOOK_AD_ACCOUNT_ID")
        if not cls.HUBSPOT_CLIENT_ID:
            missing.append("HUBSPOT_CLIENT_ID")
        if not cls.HUBSPOT_CLIENT_SECRET:
            missing.append("HUBSPOT_CLIENT_SECRET")
        if missing:
            raise RuntimeError(f"Missing required config values: {', '.join(missing)}")

# Optionally validate config at import
try:
    Config.validate()
except Exception as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    logging.error(f"Config validation error: {e}")