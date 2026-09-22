from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.state import WeatherBotState
from backend.location import geocode_city
from backend.weather import get_weather
from backend.sop_engine import find_matching_sops
from backend.responder import compose_answer


def parse_request(state: WeatherBotState):
    """Extract the city from the user's question."""

    question = state["user_question"].strip()
    words = question.replace("?", "").replace(",", "").split()

    city = None

    location_words = ["in", "at", "near", "around"]

    for i, word in enumerate(words):
        if word.lower() in location_words and i + 1 < len(words):
            city = words[i + 1]
            break

    return {
        "city": city
    }
def resolve_location(state: WeatherBotState):
    """Resolve the city to coordinates."""

    city = state.get("city")

    if not city:
        return {
            "location_error": "No city could be identified from the question."
        }

    try:
        location = geocode_city(city)

        if not location:
            return {
                "location_error": f"Could not resolve the city: {city}"
            }

        return {
            "location": location
        }

    except Exception as exc:
        return {
            "location_error": f"Location lookup failed: {exc}"
        }


def location_success(state: WeatherBotState):
    """Branch after location resolution."""

    if state.get("location"):
        return "get_weather"

    return "honest_error"


def honest_error(state: WeatherBotState):
    """Return an honest error when location resolution fails."""

    return {
        "final_answer": (
            "I could not resolve the location in your request. "
            "I cannot provide weather-based safety guidance without "
            "verified weather data."
        )
    }


def get_weather_node(state: WeatherBotState):
    """Fetch live weather for the resolved location."""

    location = state["location"]

    try:
        weather = get_weather(
            location["latitude"],
            location["longitude"],
        )

        return {
            "weather": weather
        }

    except Exception as exc:
        return {
            "weather_error": f"Weather lookup failed: {exc}"
        }


def weather_success(state: WeatherBotState):
    """Branch after the weather lookup."""

    if state.get("weather"):
        return "match_sops"

    return "honest_weather_error"


def honest_weather_error(state: WeatherBotState):
    """Return an honest error when weather lookup fails."""

    return {
        "final_answer": (
            "I could not retrieve live weather data for the resolved "
            "location. I will not invent weather conditions or safety "
            "advice."
        )
    }


def match_sops_node(state: WeatherBotState):
    """Match verified weather against SOPs relevant to the user's activity."""

    question = state["user_question"].lower()

    activity = None

    if "picnic" in question:
        activity = "picnic"
    elif "cycling" in question or "bike ride" in question or "biking" in question:
        activity = "cycling"
    elif "two-wheeler" in question or "two wheeler" in question or "scooter" in question or "motorcycle" in question:
        activity = "two_wheeler"
    elif "child" in question or "children" in question or "kid" in question:
        activity = "children"
    elif "elderly" in question or "senior citizen" in question:
        activity = "elderly"
    elif (
        "travel" in question
        or "commute" in question
        or "go to work" in question
        or "journey" in question
    ):
        activity = "travel"
    elif (
        "exercise" in question
        or "workout" in question
        or "run" in question
        or "running" in question
        or "jog" in question
        or "jogging" in question
        or "hiking" in question
    ):
        activity = "outdoor_exercise"
    else:
        activity = "general_outdoor"

    matched_sops = find_matching_sops(
        state["weather"],
        category=activity,
    )

    return {
        "matched_sops": matched_sops
    }


def sop_match_branch(state: WeatherBotState):
    """Branch depending on whether an SOP matched."""

    if state.get("matched_sops"):
        return "compose_answer"

    return "no_guidance"


def no_guidance(state: WeatherBotState):
    """Return a response when no SOP applies."""

    return {
        "final_answer": (
            "No applicable SOP was found for the verified weather "
            "conditions and scenario. I will not invent additional "
            "safety guidance."
        )
    }


def compose_answer_node(state: WeatherBotState):
    """Generate the final natural-language answer."""

    answer = compose_answer(
        user_question=state["user_question"],
        location=state["location"],
        weather=state["weather"],
        matched_sops=state["matched_sops"],
    )

    return {
        "final_answer": answer
    }


def build_graph():
    """Build the Weather Advisory LangGraph."""

    graph = StateGraph(WeatherBotState)

    graph.add_node("parse_request", parse_request)
    graph.add_node("resolve_location", resolve_location)
    graph.add_node("honest_error", honest_error)

    graph.add_node("get_weather", get_weather_node)
    graph.add_node("honest_weather_error", honest_weather_error)

    graph.add_node("match_sops", match_sops_node)
    graph.add_node("no_guidance", no_guidance)
    graph.add_node("compose_answer", compose_answer_node)

    graph.set_entry_point("parse_request")

    graph.add_edge(
        "parse_request",
        "resolve_location",
    )

    graph.add_conditional_edges(
        "resolve_location",
        location_success,
        {
            "get_weather": "get_weather",
            "honest_error": "honest_error",
        },
    )

    graph.add_conditional_edges(
        "get_weather",
        weather_success,
        {
            "match_sops": "match_sops",
            "honest_weather_error": "honest_weather_error",
        },
    )

    graph.add_conditional_edges(
        "match_sops",
        sop_match_branch,
        {
            "compose_answer": "compose_answer",
            "no_guidance": "no_guidance",
        },
    )

    graph.add_edge("honest_error", END)
    graph.add_edge("honest_weather_error", END)
    graph.add_edge("no_guidance", END)
    graph.add_edge("compose_answer", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


if __name__ == "__main__":
    app = build_graph()

    print("LangGraph compiled successfully.")
    print("Nodes:")
    print("- parse_request")
    print("- resolve_location")
    print("- get_weather")
    print("- match_sops")
    print("- compose_answer")
    print("- honest_error")
    print("- honest_weather_error")
    print("- no_guidance")