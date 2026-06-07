from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    content: str
    disease: Optional[str] = None
    symptoms: list[str] = []
    medications: list[str] = []
    treatments: list[str] = []
    outcome: Optional[str] = None


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    author_username: str
    disease: Optional[str] = None
    symptoms: list[str] = []
    medications: list[str] = []
    treatments: list[str] = []
    outcome: Optional[str] = None
    upvotes: int = 0
    created_at: datetime


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    author_id: str
    author_username: str
    created_at: datetime
