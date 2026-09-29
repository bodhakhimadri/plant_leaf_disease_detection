from backend.src.auth import get_user
from backend.src.auth import supabase

def get_reports():

    user = get_user()

    return supabase.table(
        "disease_reports"
    ).select(
        "*"
    ).eq(
        "user_id",
        user.user.id
    ).order(
        "created_at", desc=True
    ).execute().data
