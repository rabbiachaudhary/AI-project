from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from services.rag_pipeline import run_rag

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    disease: Optional[str] = None
    symptoms: Optional[list[str]] = None
    medications: Optional[list[str]] = None


class MedicalInference(BaseModel):
    predicted_disease: Optional[str]
    confidence: float
    alternatives: list[dict]
    symptoms_extracted: list[str]
    ml_used: bool


class SourceRef(BaseModel):
    ref: int
    post_id: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    score: float = 0.0


class ChatResponse(BaseModel):
    answer: str
    mode: str                              # "hybrid" | "ai_general"
    confidence: str                        # "high" | "medium" | "low"
    medical_inference: Optional[MedicalInference] = None
    sources: list[SourceRef]
    graph_used: bool
    entities_detected: dict


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = await run_rag(
        user_query=request.query,
        disease=request.disease,
        symptoms=request.symptoms or [],
        medications=request.medications or [],
    )
    return ChatResponse(**result)
