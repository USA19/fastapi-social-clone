from dotenv import load_dotenv
load_dotenv()
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.session import engine
from db.base import Base
from routes.user import router as userRouter
from routes.post import router as postRouter

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

app.include_router(userRouter)
app.include_router(postRouter)
