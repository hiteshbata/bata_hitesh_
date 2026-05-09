AVAILABLE_MODELS = {
    "anthropic": {
        "display_name": "Anthropic (Claude)",
        "models": {
            "claude-opus-4-6": {
                "display_name": "Claude Opus 4.6 (Most Powerful)",
                "cost": "expensive",
                "recommended_for": "production"
            },
            "claude-sonnet-4-6": {
                "display_name": "Claude Sonnet 4.6 (Balanced) ⭐",
                "cost": "medium",
                "recommended_for": "recommended"
            },
            "claude-haiku-4-5-20251001": {
                "display_name": "Claude Haiku 4.5 (Fastest)",
                "cost": "cheap",
                "recommended_for": "testing"
            }
        }
    }
}

DEFAULT_PROVIDER = "google"
DEFAULT_MODEL = "gemini-2.0-flash"
