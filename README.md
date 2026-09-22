# 🌦️ Weather Advisory Support Bot

A weather-advisory support bot built with **LangGraph** that provides outdoor safety guidance using live weather data and a traceable set of Standard Operating Procedures (SOPs).

The system resolves a user's location, retrieves live weather information from Open-Meteo, matches the weather and activity against YAML-based SOPs, and generates a response that references the applicable SOPs.

---

## Features

- Live weather data using Open-Meteo
- City/location resolution using Open-Meteo Geocoding
- LangGraph-based workflow with conditional branching
- YAML-based safety SOPs
- 12 configurable SOP policies
- Support for multiple activity categories
- Numeric and fuzzy policy matching
- Traceable responses with SOP IDs
- Explicit no-SOP response when no policy applies
- Honest error handling when weather data cannot be retrieved
- Session-based conversation memory
- Gemini API for language understanding and response composition
- Streamlit chat interface
- Evaluation suite covering normal, paraphrased, severe, adversarial, no-SOP, and API-failure scenarios

---

## Architecture

The application follows this LangGraph workflow:

```text
User Question
      │
      ▼
Parse Request
      │
      ▼
Resolve Location
      │
      ├────────────── Failure ──────────────► Honest Error
      │
      ▼
Get Live Weather
      │
      ├────────────── Failure ──────────────► Honest Error
      │
      ▼
Match SOPs
      │
      ├──────────── No Matching SOP ────────► No Guidance
      │
      ▼
Compose Answer
      │
      ▼
Final Answer