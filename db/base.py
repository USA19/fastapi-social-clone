# db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# alembic revision --autogenerate -m "users table updated with passowrd field"
# alembic upgrade head
