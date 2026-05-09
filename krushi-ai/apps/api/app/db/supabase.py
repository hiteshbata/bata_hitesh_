import os
from supabase import create_client, Client
from app.core.config import settings

# Provide explicit fallback to os.environ if pydantic-settings misses it during docker init
url = os.environ.get("SUPABASE_URL", settings.SUPABASE_URL)
key = os.environ.get("SUPABASE_KEY", settings.SUPABASE_KEY)

if not url or not key:
    print("WARNING: Supabase URL or Key is missing. Check your .env file or Docker environment variables.")

supabase: Client = create_client(url or "http://localhost:54321", key or "dummy")

def get_supabase_client() -> Client:
    return supabase
