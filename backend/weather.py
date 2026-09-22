import requests

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude: float, longitude: float):
    """Fetch current weather data from Open-Meteo."""

    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "precipitation,"
                "rain,"
                "wind_speed_10m,"
                "uv_index"
            ),
            "hourly": (
                "temperature_2m,"
                "precipitation_probability,"
                "precipitation,"
                "wind_speed_10m,"
                "uv_index"
            ),
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum,"
                "precipitation_probability_max,"
                "wind_speed_10m_max,"
                "uv_index_max"
            ),
            "timezone": "auto",
            "forecast_days": 1,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    latitude = 12.97194
    longitude = 77.59369

    weather = get_weather(latitude, longitude)

    print("Weather fetched successfully.")
    print("\nCurrent weather:")
    print(weather["current"])

    print("\nDaily weather:")
    print(weather["daily"])