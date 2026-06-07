from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from db.postgres import get_db
from models.pg_models import User, Profile
from models.mongo_models import PostCreate, PostResponse, CommentCreate, CommentResponse
from routers.auth import get_current_user
from services import mongo_service

router = APIRouter()


class AnalyzeRequest(BaseModel):
    title: str
    content: str


class AnalyzeResponse(BaseModel):
    disease: Optional[str] = None
    symptoms: list[str] = []
    medications: list[str] = []
    treatments: list[str] = []
    outcome: Optional[str] = None


async def _get_username(user: User, db: AsyncSession) -> str:
    result = await db.execute(select(Profile).where(Profile.user_id == user.id))
    profile = result.scalar_one_or_none()
    return profile.username if profile else user.email


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_post(
    data: AnalyzeRequest,
    _auth: User = Depends(get_current_user),
):
    from services.post_analyzer import analyze_post as _analyze
    return await _analyze(data.title, data.content)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    username = await _get_username(current_user, db)
    return await mongo_service.create_post(post, current_user.id, username)


@router.get("/", response_model=list[PostResponse])
async def list_posts(skip: int = 0, limit: int = 20):
    return await mongo_service.get_posts(skip=skip, limit=min(limit, 50))


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    post = await mongo_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: str,
    data: PostCreate,
    current_user: User = Depends(get_current_user),
):
    post = await mongo_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only edit your own posts")
    updated = await mongo_service.update_post(post_id, data)
    if not updated:
        raise HTTPException(status_code=500, detail="Update failed")
    return updated


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
):
    post = await mongo_service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    await mongo_service.delete_post(post_id)


@router.post("/{post_id}/upvote")
async def upvote(post_id: str, current_user: User = Depends(get_current_user)):
    result = await mongo_service.upvote_post(post_id, str(current_user.id))
    if result == "not_found":
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Already upvoted" if result == "already" else "Upvoted", "already": result == "already"}


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: str,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    username = await _get_username(current_user, db)
    return await mongo_service.add_comment(post_id, comment, current_user.id, username)


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_comments(post_id: str):
    return await mongo_service.get_comments(post_id)


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    _post_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
):
    deleted = await mongo_service.delete_comment(comment_id, str(current_user.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Comment not found or not yours")
