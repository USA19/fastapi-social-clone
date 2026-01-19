import uuid
from sqlalchemy import (
    Column, Text, DateTime, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from datetime import datetime
from db.base import Base
import enum


class PostVisibility(enum.Enum):
    public = "public"
    friends = "friends"
    private = "private"


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=False)
    media_url = Column(Text, nullable=True)

    visibility = Column(
        ENUM(PostVisibility, name='postvisibility'),
        default=PostVisibility.public,
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
    )

    author = relationship("User", back_populates="posts")
