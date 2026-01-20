from pydantic import BaseModel
from typing import Optional
from enum import Enum
from uuid import UUID
from datetime import datetime
from .user import UserOutput
class PostVisibility(str, Enum):
    public = "public"
    friends = "friends"
    private = "private"

class CreatePostInput(BaseModel):
    content: str
    media_url: Optional[str] = None
    visibility: PostVisibility = PostVisibility.public

class PostSchema(BaseModel):
    id: UUID
    content: str
    media_url: Optional[str]
    visibility: PostVisibility
    created_at: datetime
    updated_at: datetime
    author: Optional[UserOutput] = None
    class Config:
        from_attributes = True

class PostOutput(BaseModel):
    post:Optional[PostSchema]
    message:str
    class Config:
      from_attributes = True

class PaginatedPostsResponse(BaseModel):
    page: int
    limit: int
    totalCount: int
    posts: list[PostSchema]
    totalPages: int