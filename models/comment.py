# models/comment.py
from sqlalchemy import Column, String, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.base import Base
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)

    # Relationships
    userId = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    postId = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    parentId = Column(UUID(as_uuid=True), ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # SQLAlchemy relationships
    user = relationship("User", backref="comments")
    post = relationship("Post", backref="comments")
    # Replies: child comments that have this comment as their parent
    # 🔥 FIXED self-referential relationships
    parent = relationship(
        "Comment",
        remote_side=[id],
        back_populates="replies"
    )

    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
