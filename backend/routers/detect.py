from fastapi import APIRouter, UploadFile, File, HTTPException

from services.skin_detector import detect_skin_disease
from services.rag_pipeline import run_rag

router = APIRouter()

_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}


@router.post("/")
async def detect_and_explain(image: UploadFile = File(...)):
    """
    1. Send image to HF Space skin disease classifier
    2. Take the top predicted disease
    3. Run it through the RAG pipeline (KB + community posts + graph)
    4. Return detection result + full RAG answer
    """
    if image.content_type not in _ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="File must be a JPEG, PNG, or WebP image")

    image_bytes = await image.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image must be under 10 MB")

    # ── Step 1: Detect disease via HF Space ──────────────────────────────────
    try:
        detection = await detect_skin_disease(image_bytes, image.filename or "image.jpg")
    except Exception as e:
        print(f"[detect] HF Space error: {e}")
        raise HTTPException(status_code=502, detail=f"Skin detection service unavailable: {e}")

    disease = detection.get("disease")
    if not disease:
        raise HTTPException(
            status_code=422,
            detail="Could not detect a recognisable skin condition from this image. Try a clearer, closer photo.",
        )

    # ── Step 2: Feed detection into RAG pipeline ──────────────────────────────
    query = (
        f"I have been diagnosed with {disease}. "
        "What should I know about this skin condition — its causes, symptoms, treatments, "
        "and what have others in the community experienced with it?"
    )
    rag_result = await run_rag(user_query=query, disease=disease)

    return {
        "detection": detection,
        "rag": rag_result,
    }
