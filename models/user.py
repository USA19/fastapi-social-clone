import uuid
from sqlalchemy import Column, UUID, String, Boolean
from db.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    email = Column(String, unique=True, index=True)
    firstName = Column(String)
    lastName = Column(String)
    is_active = Column(Boolean, default=False)
    password = Column(String)
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan"
    )