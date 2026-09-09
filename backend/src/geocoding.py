from geopy.geocoders import Nominatim


def get_address(latitude, longitude):

    try:

        geolocator = Nominatim(
            user_agent="agridoctor_ai"
        )

        location = geolocator.reverse(
            f"{latitude}, {longitude}"
        )

        address = location.raw["address"]

        return {
            "state": address.get("state"),
            "district": (
                address.get("county")
                or address.get("state_district")
            )
        }

    except Exception:

        return {
            "state": "Unknown",
            "district": "Unknown"
        }