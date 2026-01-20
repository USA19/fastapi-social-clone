# db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# from models.user import User
# from models.post import Post

# alembic revision --autogenerate -m "users table updated with passowrd field"
# alembic upgrade head
