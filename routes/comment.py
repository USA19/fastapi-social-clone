# routes/comment.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload
from db.session import get_db
from models.comment import Comment
from models.user import User
from models.post import Post
from schemas.comment import CreateCommentInput,CommentOutput,CommentsOutput
from middleware.auth import get_current_user
from uuid import UUID

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.get("/posts/{postId}", response_model=CommentsOutput)
def get_comments(postId: UUID, db: Session = Depends(get_db)):
    comments = (
        db.query(Comment)
        .options(joinedload(Comment.user), joinedload(Comment.replies).joinedload(Comment.user))
        .filter(Comment.postId == postId, Comment.parentId == None)
        .all()
    )
    return {"comment": comments, "message": "Comments fetched successfully"}


@router.post("/posts/{postId}", response_model=CommentOutput)
def add_comment(
    postId: UUID,
    comment: CreateCommentInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if post exists
    post = db.get(Post, postId)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # If parentId is provided, ensure it exists and is a first-level comment
    parentComment = None
    if comment.parentId:
        parentComment = db.get(Comment, comment.parentId)
        if not parentComment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        # prevent nesting beyond 2 levels
        if parentComment.parentId:
            raise HTTPException(status_code=400, detail="Cannot reply beyond 2 levels")

    # Create comment
    new_comment = Comment(
        content=comment.content,
        userId=current_user.id,
        postId=post.id,
        parentId=comment.parentId
    )

    db.add(new_comment)
    db.commit()
    
    # Reload comment with user relationship
    # For a new comment, we don't need to load replies (it will be empty)
    new_comment = (
        db.query(Comment)
        .options(joinedload(Comment.user), joinedload(Comment.replies).joinedload(Comment.user))
        .filter(Comment.id == new_comment.id)
        .first()
    )
    
    return {"comment": new_comment, "message": "Comment added successfully"}
