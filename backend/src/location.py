import geocoder


def get_current_location():

    try:

        g = geocoder.ip("me")

        return {
            "latitude": g.latlng[0],
            "longitude": g.latlng[1],
            "city": g.city,
            "state": g.state,
            "country": g.country
        }

    except Exception:

        return None
    