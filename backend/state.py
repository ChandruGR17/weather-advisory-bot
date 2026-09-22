from typing import TypedDict, Optional, Any


class WeatherBotState(TypedDict, total=False):
    user_question: str

    city: Optional[str]

    location: Optional[dict]
    location_error: Optional[str]

    weather: Optional[dict]
    weather_error: Optional[str]

    matched_sops: list[dict]

    final_answer: str