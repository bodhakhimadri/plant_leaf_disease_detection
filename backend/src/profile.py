from backend.src.database import supabase


def create_profile(
    user_id,
    email,
    state,
    district,
    latitude,
    longitude
):

    return (
        supabase
        .table("user_profiles")
        .upsert(
            {
                "id": user_id,
                "email": email,
                "state": state,
                "district": district,
                "latitude": latitude,
                "longitude": longitude
            }
        )
        .execute()
    )


def get_profile(user_id):

    response = (
        supabase
        .table("user_profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    return response.data if response is not None else None


def update_profile(
    user_id,
    state,
    district,
    latitude,
    longitude
):

    return (
        supabase
        .table("user_profiles")
        .update(
            {
                "state": state,
                "district": district,
                "latitude": latitude,
                "longitude": longitude
            }
        )
        .eq("id", user_id)
        .execute()
    )
