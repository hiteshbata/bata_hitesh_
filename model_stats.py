# Module-level dictionary to track usage.
# Format: {"provider:model": count}
model_stats: dict[str, int] = {}

def increment_stat(provider: str, model: str):
    """Increments the usage count for a specific provider and model."""
    key = f"{provider}:{model}"
    model_stats[key] = model_stats.get(key, 0) + 1

def get_stats() -> dict[str, int]:
    """Returns the current model usage stats."""
    return dict(model_stats)

def format_stats_message() -> str:
    """Formats the current stats into a Telegram-friendly message."""
    if not model_stats:
        return "📊 Model Usage Stats\n(Resets on restart)\n\nNo models have been used yet this session."

    lines = ["📊 Model Usage Stats", "(Resets on restart)\n"]

    # Group by provider
    grouped = {}
    for key, count in model_stats.items():
        provider, model = key.split(":", 1)
        if provider not in grouped:
            grouped[provider] = []
        grouped[provider].append((model, count))

    provider_icons = {
        "google": "🌟 Google",
        "anthropic": "🤖 Anthropic",
        "openrouter": "🔀 OpenRouter",
        "openai": "🧠 OpenAI"
    }

    total = 0
    for provider, models in grouped.items():
        icon = provider_icons.get(provider, f"📦 {provider.capitalize()}")
        lines.append(f"{icon}")
        for model, count in models:
            lines.append(f"  {model}: {count} messages")
            total += count
        lines.append("") # Empty line for spacing

    lines.append(f"Total: {total} messages this session")
    return "\n".join(lines)
