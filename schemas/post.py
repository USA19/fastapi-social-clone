from pydantic import BaseModel
from typing import Optional
from enum import Enum
from uuid import UUID
from datetime import datetime

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

    class Config:
        from_attributes = True

class PostOutput(BaseModel):
    post:PostSchema
    message:str
    class Config:
      from_attributes = True