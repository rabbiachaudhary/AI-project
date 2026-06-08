import json
import re

from services.openrouter_service import generate_response

_PROMPT = """You are a dermatology NLP assistant for DermaCom, a skin disease community platform.
Extract structured information from this skin condition experience post.

Return ONLY a valid JSON object — no explanation, no markdown, just raw JSON:
{{
  "disease": "skin condition name (e.g. Acne, Psoriasis, Eczema, Rosacea, Vitiligo), or null",
  "symptoms": ["skin symptom1", "skin symptom2"],
  "medications": ["topical or oral drug name"],
  "treatments": ["non-medication skin treatment"],
  "outcome": "one short phrase like Cleared / Improved / Ongoing / Worsened, or null"
}}

Rules:
- disease: the main skin condition. null if none mentioned.
- symptoms: skin-related complaints only (e.g. "Itching", "Rash", "Redness", "Dryness", "Blisters", "Scaling", "Pimples").
- medications: drug/cream/gel names (e.g. "Benzoyl peroxide", "Hydrocortisone", "Clotrimazole", "Doxycycline").
- treatments: non-drug interventions (e.g. "Moisturising", "Sun protection", "Phototherapy", "Cold compress").
- outcome: how the skin condition resolved or progressed, or null.
- Return [] for any list with nothing.

Post title: {title}
Post content: {content}

JSON:"""


async def analyze_post(title: str, content: str) -> dict:
    """Use LLM to extract disease, symptoms, medications, treatments, outcome from post text."""
    prompt = _PROMPT.format(title=title, content=content)
    try:
        raw = (await generate_response(prompt)).strip()
        # Extract JSON even if wrapped in markdown code block
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        data = json.loads(match.group(0) if match else raw)
        return {
            "disease": (data.get("disease") or "").strip() or None,
            "symptoms": [s.strip() for s in (data.get("symptoms") or []) if isinstance(s, str) and s.strip()][:12],
            "medications": [m.strip() for m in (data.get("medications") or []) if isinstance(m, str) and m.strip()][:10],
            "treatments": [t.strip() for t in (data.get("treatments") or []) if isinstance(t, str) and t.strip()][:10],
            "outcome": (data.get("outcome") or "").strip() or None,
        }
    except Exception:
        return {"disease": None, "symptoms": [], "medications": [], "treatments": [], "outcome": None}
