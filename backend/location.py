import requests


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def geocode_city(city: str):
    """Resolve a city name to latitude and longitude."""

    response = requests.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()
    results = data.get("results", [])

    if not results:
        return None

    result = results[0]

    return {
        "name": result.get("name"),
        "country": result.get("country"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
    }


if __name__ == "__main__":
    city = "Bengaluru"
    location = geocode_city(city)

    if location:
        print("Location found:")
        print(location)
    else:
        print("Location not found.")