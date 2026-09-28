from supabase import create_client, Client
from .config import settings

if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
    supabase: Client | None = None
else:
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
