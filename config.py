import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load env variables
load_dotenv()

class Settings:
    MODE = os.getenv("MODE", "polling")
    PORT = int(os.getenv("PORT", 8000))

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Local Business")
    BUSINESS_ID = os.getenv("BUSINESS_ID", "local_business")

settings = Settings()

ACTIVE_MODEL_FILE = "active_model.json"

def validate_required_env_vars():
    """Validates that required environment variables are set."""
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("Missing required environment variable: TELEGRAM_BOT_TOKEN")

    if not settings.OPENAI_API_KEY:
        raise ValueError("Missing required environment variable: OPENAI_API_KEY (needed for embeddings)")

    if settings.MODE == "webhook" and not settings.WEBHOOK_URL:
        raise ValueError("Missing required environment variable: WEBHOOK_URL (required in webhook mode)")

    if not any([settings.GOOGLE_API_KEY, settings.OPENROUTER_API_KEY, settings.ANTHROPIC_API_KEY, settings.OPENAI_API_KEY]):
        logging.warning("WARNING: No LLM provider API key found. Bot will fail on first message.")

# Run validation at import time
validate_required_env_vars()

def load_active_model() -> dict:
    """Loads the active model from the config file, creating it if it doesn't exist."""
    if not Path(ACTIVE_MODEL_FILE).exists():
        # First run - create with defaults
        # We import here to avoid circular imports if models_config uses config
        from models_config import DEFAULT_PROVIDER, DEFAULT_MODEL
        default = {
            "provider": DEFAULT_PROVIDER,
            "model": DEFAULT_MODEL,
            "changed_at": None,
            "changed_by": "system_default"
        }
        with open(ACTIVE_MODEL_FILE, "w") as f:
            json.dump(default, f, indent=2)
        return default

    with open(ACTIVE_MODEL_FILE, "r") as f:
        return json.load(f)

def save_active_model(provider: str, model: str, changed_by: str = "admin", changed_at: str = None):
    """Saves the active model configuration to the config file."""
    import datetime

    if changed_at is None:
        changed_at = datetime.datetime.utcnow().isoformat()

    config = {
        "provider": provider,
        "model": model,
        "changed_at": changed_at,
        "changed_by": str(changed_by)
    }
    with open(ACTIVE_MODEL_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return config
