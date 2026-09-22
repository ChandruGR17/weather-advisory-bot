from pathlib import Path
import yaml


SOP_FILE = Path(__file__).parent / "policies" / "sops.yaml"


def load_sops():
    """Load SOP policies from the YAML file."""
    with open(SOP_FILE, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    return data["sops"]


def compare_value(actual, operator, expected):
    """Compare a weather value against an SOP threshold."""

    if actual is None:
        return False

    if operator == ">=":
        return actual >= expected

    if operator == ">":
        return actual > expected

    if operator == "<=":
        return actual <= expected

    if operator == "<":
        return actual < expected

    if operator == "==":
        return actual == expected

    return False


def get_weather_value(weather, metric):
    """Get a requested metric from the Open-Meteo response."""

    current = weather.get("current", {})
    daily = weather.get("daily", {})

    # Current weather values
    current_values = {
        # Temperature
        "temperature": current.get("temperature_2m"),
        "temperature_2m": current.get("temperature_2m"),

        # Precipitation
        "precipitation": current.get("precipitation"),

        # Wind
        "wind_speed": current.get("wind_speed_10m"),
        "wind_speed_10m": current.get("wind_speed_10m"),

        # UV
        "uv_index": current.get("uv_index"),
    }

    # Daily weather values
    daily_values = {
        "temperature_max": daily.get(
            "temperature_2m_max", [None]
        )[0],

        "temperature_2m_max": daily.get(
            "temperature_2m_max", [None]
        )[0],

        "precipitation_sum": daily.get(
            "precipitation_sum", [None]
        )[0],

        "precipitation_probability": daily.get(
            "precipitation_probability_max", [None]
        )[0],

        "precipitation_probability_max": daily.get(
            "precipitation_probability_max", [None]
        )[0],

        "wind_speed_max": daily.get(
            "wind_speed_10m_max", [None]
        )[0],

        "wind_speed_10m_max": daily.get(
            "wind_speed_10m_max", [None]
        )[0],

        "uv_index_max": daily.get(
            "uv_index_max", [None]
        )[0],
    }

    if metric in current_values:
        return current_values[metric]

    if metric in daily_values:
        return daily_values[metric]

    return None


def matches_numeric_condition(condition, weather):
    """Check one numeric condition."""

    metric = condition.get("metric")
    operator = condition.get("operator")
    expected = condition.get("value")

    actual = get_weather_value(weather, metric)

    return compare_value(actual, operator, expected)


def matches_threshold_rule(actual, rule):
    """
    Check a YAML threshold rule.

    Supported formats:
        min: 40
        max: 30
    """

    if actual is None:
        return False

    if not isinstance(rule, dict):
        return False

    if "min" in rule:
        if actual < rule["min"]:
            return False

    if "max" in rule:
        if actual > rule["max"]:
            return False

    return True


def matches_sop(sop, weather):
    """
    Check whether an SOP matches the current weather.

    Supports:
    - Numeric min/max conditions
    - OR conditions using 'any'
    - Fuzzy SOPs
    - activity_categories
    """

    conditions = sop.get("conditions", {})

    # Fuzzy SOPs are handled by category matching.
    # Example: SOP-012 Picnic Suitability.
    if sop.get("fuzzy") is True:
        return True

    if not isinstance(conditions, dict):
        return False

    # ---------------------------------------------------------
    # Handle OR conditions
    # Example:
    #
    # any:
    #   - precipitation:
    #       min: 5
    #   - wind_speed_10m:
    #       min: 40
    # ---------------------------------------------------------

    if "any" in conditions:

        any_conditions = conditions.get("any", [])

        for condition in any_conditions:

            if not isinstance(condition, dict):
                continue

            for metric, rule in condition.items():

                actual = get_weather_value(weather, metric)

                if matches_threshold_rule(actual, rule):
                    return True

        return False

    # ---------------------------------------------------------
    # Handle normal numeric conditions
    # ---------------------------------------------------------

    for metric, rule in conditions.items():

        # Activity categories are used for filtering.
        # They are NOT weather conditions.
        if metric == "activity_categories":
            continue

        if not isinstance(rule, dict):
            continue

        actual = get_weather_value(weather, metric)

        if not matches_threshold_rule(actual, rule):
            return False

    return True


def find_matching_sops(weather, category=None):
    """Return all SOPs that match the current weather."""

    sops = load_sops()
    matched = []

    for sop in sops:

        # -----------------------------------------------------
        # Filter by activity category
        # -----------------------------------------------------

        if category:

            conditions = sop.get("conditions", {})

            activity_categories = conditions.get(
                "activity_categories", []
            )

            if category not in activity_categories:
                continue

        # -----------------------------------------------------
        # Check weather conditions
        # -----------------------------------------------------

        if matches_sop(sop, weather):
            matched.append(sop)

    return matched


if __name__ == "__main__":

    # Import weather module when running this file directly.
    from weather import get_weather

    latitude = 12.97194
    longitude = 77.59369

    weather = get_weather(latitude, longitude)

    matched = find_matching_sops(weather)

    print(f"Matched {len(matched)} SOP(s):")

    for sop in matched:
        print(f"- {sop['id']}: {sop['name']}")