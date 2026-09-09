from datetime import datetime, timedelta

from backend.src.database import supabase
from backend.src.auth import get_user


def get_reports():

    user = get_user()

    reports = (
        supabase
        .table("disease_reports")
        .select("*")
        .eq("user_id", user.user.id)
        .order("created_at", desc=True)
        .execute()
    )

    return reports.data

def get_dashboard_stats():

    reports = get_reports()

    total = len(reports)

    healthy = 0
    diseased = 0

    for report in reports:

        disease = report["disease_name"].lower()

        if "healthy" in disease:

            healthy += 1

        else:

            diseased += 1

    return {

        "total_predictions": total,

        "healthy": healthy,

        "diseased": diseased
    }

def get_recent_predictions(limit=5):

    reports = get_reports()

    return reports[:limit]

from collections import Counter


def get_disease_distribution():

    reports = get_reports()

    diseases = []

    for report in reports:

        diseases.append(
            report["disease_name"]
        )

    return Counter(diseases)

def get_top_diseases(limit=5):

    distribution = get_disease_distribution()

    return distribution.most_common(limit)

def get_predictions_by_day():

    reports = get_reports()

    today = datetime.now()

    result = {}

    for i in range(6, -1, -1):

        day = (
            today - timedelta(days=i)
        ).strftime("%Y-%m-%d")

        result[day] = 0

    for report in reports:

        date = report["created_at"][:10]

        if date in result:

            result[date] += 1

    return result


def get_total_users():

    users = (
        supabase
        .table("user_profiles")
        .select("id", count="exact")
        .execute()
    )

    return users.count

def get_total_reports():

    reports = (
        supabase
        .table("disease_reports")
        .select("id", count="exact")
        .execute()
    )

    return reports.count

def get_total_diseases():

    reports = (
        supabase
        .table("disease_reports")
        .select("disease_name")
        .execute()
        .data
    )

    diseases = set()

    for report in reports:

        diseases.add(
            report["disease_name"]
        )

    return len(diseases)


from backend.src.alerts import get_disease_alerts
def get_active_alerts():

    alerts = get_disease_alerts()

    return len(alerts)


def get_community_stats():

    return {

        "users": get_total_users(),

        "reports": get_total_reports(),

        "diseases": get_total_diseases(),

        "alerts": get_active_alerts()
    }