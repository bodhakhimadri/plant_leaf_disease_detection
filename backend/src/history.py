from supabase import create_client
import os
from dotenv import load_dotenv
from backend.src.auth import get_user

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

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