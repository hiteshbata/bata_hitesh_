import logging
import httpx
import google.generativeai as genai
from typing import List, Dict, Any

from config import settings
from models_config import AVAILABLE_MODELS

# OpenRouter allowed providers and hard limits
OPENROUTER_ALLOWED_PROVIDERS = [
    "meta-llama",
    "mistralai",
    "deepseek",
    "google",
    "microsoft",
    "qwen",
    "anthropic",
    "openai"
]

OPENAI_ALLOWED_PREFIXES = [
    "gpt-4o",
    "gpt-4-turbo",
    "o1",
    "o3",
    "gpt-3.5-turbo"
]

OPENAI_BLOCKED_KEYWORDS = [
    "instruct", "embedding", "whisper",
    "dall-e", "tts", "realtime", "audio",
    "search", "computer-use"
]

async def fetch_openrouter_models() -> List[Dict[str, str]]:
    """Live fetches OpenRouter models and filters by allowed providers, returning max 50."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://openrouter.ai/api/v1/models")
            response.raise_for_status()
            data = response.json()

            models = data.get("data", [])
            filtered = []

            for m in models:
                model_id = m.get("id", "")
                provider_prefix = model_id.split("/")[0] if "/" in model_id else ""

                if provider_prefix in OPENROUTER_ALLOWED_PROVIDERS:
                    # Also consider price filtering here if desired (e.g. m.get("pricing", {}).get("prompt", 0))
                    filtered.append({
                        "id": model_id,
                        "label": m.get("name", model_id)
                    })

            return filtered[:50]
    except Exception as e:
        logging.error(f"Error fetching OpenRouter models: {e}")
        return []

async def fetch_openai_models() -> List[Dict[str, str]]:
    """Live fetches OpenAI models and filters by allowed prefixes and blocked keywords."""
    if not settings.OPENAI_API_KEY:
        return []

    try:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
            response = await client.get("https://api.openai.com/v1/models", headers=headers)
            response.raise_for_status()
            data = response.json()

            models = data.get("data", [])
            filtered = []

            for m in models:
                model_id = m.get("id", "")

                # Check prefixes
                if not any(model_id.startswith(prefix) for prefix in OPENAI_ALLOWED_PREFIXES):
                    continue

                # Check blocked keywords
                if any(keyword in model_id.lower() for keyword in OPENAI_BLOCKED_KEYWORDS):
                    continue

                filtered.append({
                    "id": model_id,
                    "label": model_id
                })

            return filtered
    except Exception as e:
        logging.error(f"Error fetching OpenAI models: {e}")
        return []

async def fetch_google_models() -> List[Dict[str, str]]:
    """Live fetches Google Gemini models."""
    if not settings.GOOGLE_API_KEY:
        return []

    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        # Using list_models from genai package
        models = [m for m in genai.list_models() if "generateContent" in m.supported_generation_methods]

        filtered = []
        for m in models:
            model_id = m.name.replace("models/", "")
            filtered.append({
                "id": model_id,
                "label": m.display_name or model_id
            })

        return filtered
    except Exception as e:
        logging.error(f"Error fetching Google models: {e}")
        return []

def get_anthropic_models() -> List[Dict[str, str]]:
    """Returns the static list of Anthropic models from configuration."""
    anthropic_dict = AVAILABLE_MODELS.get("anthropic", {}).get("models", {})
    return [{"id": k, "label": v["display_name"]} for k, v in anthropic_dict.items()]

async def get_all_providers_models() -> Dict[str, List[Dict[str, str]]]:
    """Fetches all models across all supported providers."""
    return {
        "anthropic": get_anthropic_models(),
        "openai": await fetch_openai_models(),
        "google": await fetch_google_models(),
        "openrouter": await fetch_openrouter_models()
    }
