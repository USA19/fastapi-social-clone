from fastapi import APIRouter, Form,Query,File,UploadFile,HTTPException
from schemas.post import PostOutput,PaginatedPostsResponse
from fastapi import Depends
from db.session import get_db  
from middleware.auth import get_current_user
from middleware.file import validateUpload
from models.post import Post
from models.user import User
from sqlalchemy.orm import Session,joinedload
import math
import shutil
import os
import uuid

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostOutput)
def create_post(
    content: str = Form(...),
    visibility: str = Form("public"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile | None = Depends(validateUpload),
):
    media_url = None
    if file:
        # generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4().hex}{file_ext}"
        media_url = os.path.join("uploads", file_name)

        # save file locally
        with open(media_url, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    post = Post(
        content=content,
        visibility=visibility,
        userId=current_user.id,
        media_url=f"/uploads/{file_name}" if file else None,
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

@router.put("/{postId}", response_model=PostOutput)
async def update_post(
    postId: str,
    content: str = Form(...),
    visibility: str = Form("public"),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.get(Post, postId)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update content & visibility
    post.content = content
    post.visibility = visibility

    # Handle file upload
    if file:
        # Remove old file if exists
        if post.media_url:
             oldFilename = os.path.basename(post.media_url)
             oldFilePath = os.path.join("uploads", oldFilename)
             if os.path.exists(oldFilePath):
                os.remove(oldFilePath)
        # Save new file
        file_ext = os.path.splitext(file.filename)[1]
        file_name = f"{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join("uploads", file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        post.media_url = file_path

    db.add(post)
    db.commit()
    db.refresh(post)

    return {
       "post": post,
        "message": "Post updated successfully"
    }

@router.delete("/{postId}",response_model=PostOutput)
async def delete_post(
    postId: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.get(Post, postId)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete file if exists
    if post.media_url:
        oldFilename = os.path.basename(post.media_url)
        oldFilePath = os.path.join("uploads", oldFilename)
        if os.path.exists(oldFilePath):
            os.remove(oldFilePath)

    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully", "post":None}