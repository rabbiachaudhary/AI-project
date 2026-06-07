"""
Detects skin disease from an image using a vision LLM via OpenRouter.
Model: meta-llama/llama-3.2-11b-vision-instruct:free

Sends the image as a base64 data URL alongside a structured prompt.
The LLM identifies the condition and returns JSON — which is then fed
directly into the RAG pipeline as a disease hint.
"""

import base64
import json
import re

from services.openrouter_service import _get_client

# Try these in order — first one that works is used
_VISION_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen2-vl-7b-instruct:free",
    "google/gemini-flash-1.5-8b",
]

_SKIN_CONDITIONS = [
    "Acne", "Psoriasis", "Eczema", "Contact Dermatitis", "Rosacea",
    "Vitiligo", "Seborrheic Dermatitis", "Ringworm", "Scabies",
    "Urticaria", "Herpes Zoster", "Melanoma", "Warts", "Impetigo",
    "Chickenpox", "Drug Reaction", "Fungal Infection", "Allergy",
]

_PROMPT = f"""You are a dermatology AI assistant. Analyze this skin image carefully and identify the condition shown.

Respond ONLY with valid JSON in this exact format — no extra text before or after:
{{
    "disease": "condition name or null",
    "confidence": 0.85,
    "reasoning": "brief description of the visual features you see",
    "all_predictions": [
        {{"disease": "most likely condition", "confidence": 0.85}},
        {{"disease": "second possibility", "confidence": 0.10}}
    ]
}}

Choose the disease from this list only: {", ".join(_SKIN_CONDITIONS)}

If the image does not show a skin condition clearly, set disease to null and confidence to 0."""


async def detect_skin_disease(image_bytes: bytes, filename: str = "image.jpg") -> dict:
    """
    Send image to vision LLM → get disease prediction → return structured dict.

    Returns:
        {
            "disease": str | None,
            "confidence": float,
            "reasoning": str,
            "all_predictions": [{"disease": str, "confidence": float}, ...]
        }
    """
    content_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    encoded = base64.b64encode(image_bytes).decode()
    data_url = f"data:{content_type};base64,{encoded}"

    client = _get_client()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": data_url}},
                {"type": "text", "text": _PROMPT},
            ],
        }
    ]

    last_error = None
    for model in _VISION_MODELS:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=400,
            )
            content = response.choices[0].message.content or ""
            print(f"[skin_detector] used model: {model}")
            return _parse(content)
        except Exception as e:
            print(f"[skin_detector] {model} failed: {e}")
            last_error = e

    raise RuntimeError(f"All vision models failed. Last error: {last_error}")


def _parse(content: str) -> dict:
    # Extract JSON block from response (LLM sometimes adds markdown fences)
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if not match:
        return {"disease": None, "confidence": 0.0, "reasoning": content, "all_predictions": []}

    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return {"disease": None, "confidence": 0.0, "reasoning": content, "all_predictions": []}

    disease = data.get("disease")
    if isinstance(disease, str) and disease.lower() in ("null", "none", "unknown", ""):
        disease = None

    return {
        "disease": disease,
        "confidence": round(float(data.get("confidence", 0.0)), 3),
        "reasoning": data.get("reasoning", ""),
        "all_predictions": data.get("all_predictions", []),
    }
