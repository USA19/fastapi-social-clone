from fastapi import APIRouter,Query
from schemas.post import PostOutput,CreatePostInput,PaginatedPostsResponse
from fastapi import Depends
from db.session import get_db  
from auth.jwt import get_current_user
from models.post import Post
from models.user import User
from sqlalchemy.orm import Session,joinedload
import math

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

@router.get("/", response_model=PaginatedPostsResponse)
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit

    total = db.query(Post).count()
    totalPages = math.ceil(total / limit) if total > 0 else 1
    posts = (
        db.query(Post)
        .options(joinedload(Post.author))  # prevents N+1 queries
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "totalCount": total,
        "posts": posts,
        "totalPages": totalPages
    }
