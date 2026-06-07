from fastapi import APIRouter
from pydantic import BaseModel

from services.mongo_service import vector_search, keyword_search

router = APIRouter()


class SearchResponse(BaseModel):
    results: list[dict]
    count: int


@router.get("/", response_model=SearchResponse)
async def semantic_search(q: str, limit: int = 10):
    lim = min(limit, 20)
    results = await vector_search(q, limit=lim)
    if not results:
        results = await keyword_search(q, limit=lim)
    return SearchResponse(results=results, count=len(results))
