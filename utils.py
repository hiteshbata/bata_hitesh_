def format_response_time(ms: float) -> str:
    """Formats response time in milliseconds to a human-readable string."""
    if ms < 1000:
        return f"{int(ms)}ms"
    else:
        return f"{ms / 1000:.2f}s"

def truncate_text(text: str, max_len: int) -> str:
    """Truncates text to a maximum length with an ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."

def is_admin(telegram_user_id: int) -> bool:
    """Checks if a user is an admin by comparing against config."""
    # Lazy import config at function call time to avoid circular imports
    from config import settings
    return str(telegram_user_id) == str(settings.ADMIN_TELEGRAM_ID)
