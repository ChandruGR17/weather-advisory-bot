import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def compose_answer(
    user_question: str,
    location: dict | None = None,
    weather: dict | None = None,
    matched_sops: list[dict] | None = None
) -> str:
    """
    Compose the final response using verified weather data
    and deterministic SOP matches.

    The LLM only writes the answer.
    It does not decide which policy applies.
    """

    if not matched_sops:
        return (
            "I could not find an applicable SOP for this request. "
            "I don't have policy-based guidance for this situation."
        )

    sop_text = "\n\n".join(
        [
            f"SOP ID: {sop['id']}\n"
            f"Name: {sop['name']}\n"
            f"Category: {sop['category']}\n"
            f"Severity: {sop['severity']}\n"
            f"Advice: {sop['advice']}"
            for sop in matched_sops
        ]
    )

    prompt = f"""
You are the response-writing component of a weather safety support bot.

IMPORTANT:
- You do NOT decide whether an SOP applies.
- The application code has already selected the SOPs.
- Use ONLY the weather values provided below.
- Never invent weather values.
- Never estimate or guess missing weather values.
- Never create safety advice that is not supported by the supplied SOPs.
- Clearly mention the applicable SOP ID.
- Keep the answer concise and understandable.
- If multiple SOPs apply, mention them.
- The weather data comes from a live weather API.

USER QUESTION:
{user_question}

VERIFIED WEATHER DATA:
{weather}

APPLICABLE SOPs:
{sop_text}

Write the final answer for the user.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text.strip()


if __name__ == "__main__":
    print("Gemini responder module imported successfully.")