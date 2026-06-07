from services.openrouter_service import generate_response

_SYSTEM_HINT = (
    "You are a dermatology NLP assistant for a skin disease platform. "
    "Extract every skin-related symptom or complaint from the user's text. "
    "Return ONLY a comma-separated list of skin symptoms "
    "(e.g. 'itching, rash, redness, dry skin, blisters, scaling, pimples'). "
    "No explanations. If none found, reply: none"
)


async def extract_symptoms(text: str) -> list[str]:
    """Use LLM to extract symptom list from free-form user text."""
    prompt = f"{_SYSTEM_HINT}\n\nUser text: {text}\n\nSymptoms:"
    try:
        raw = await generate_response(prompt)
        raw = raw.strip()
        if not raw or raw.lower() == "none":
            return []
        symptoms = [s.strip().lower() for s in raw.split(",") if s.strip()]
        # Guard against garbage long strings
        return [s for s in symptoms if 1 < len(s) < 60][:15]
    except Exception:
        return []
