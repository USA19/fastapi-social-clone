# schemas/comment.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime
from .user import UserOutput  # assuming you already have a user output schema

class Comment(BaseModel):
    id: UUID
    content: str
    user: UserOutput
    postId: UUID
    parentId: Optional[UUID] = None
    replies: List["Comment"] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class CreateCommentInput(BaseModel):
    content: str
    parentId: Optional[UUID] = None

class CommentOutput(BaseModel):
    comment: Comment
    message: str

class CommentsOutput(BaseModel):
    comment: list[Comment]
    message: str