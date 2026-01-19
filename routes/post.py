from fastapi import APIRouter
from schemas.post import PostOutput,CreatePostInput
from fastapi import Depends
from db.session import get_db  
from auth.jwt import get_current_user
from models.post import Post
from models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostOutput)
def create_post(
    payload: CreatePostInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = Post(
        **payload.model_dump(),
        userId=current_user.id,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return {"post": post, "message": "Post created successfully"}
