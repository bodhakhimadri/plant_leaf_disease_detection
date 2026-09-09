from backend.src.database import supabase
from backend.src.auth import get_user
from datetime import datetime, timezone
from backend.src.profile import get_profile
from backend.src.logger import log_event


def save_report(disease_name, confidence, report):
    user = get_user()
    user_id = user.user.id
    profile = get_profile(user_id)

    if profile is None:
        raise ValueError(
            "Your profile is missing. Run the user-profile backfill SQL migration "
            "in Supabase, then sign out and sign in again."
        )

    data = {
        "user_id": user_id,
        "disease_name": disease_name,
        "confidence": confidence,
        "report": report,
        "state": profile["state"],
        "district": profile["district"],
        "latitude": profile["latitude"],
        "longitude": profile["longitude"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    response = supabase.table(
        "disease_reports"
    ).insert(
        data
    ).execute()

    log_event(
        "REPORT GENERATED",
        {
            "disease": disease_name
        }
    )
    return response
