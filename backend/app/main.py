from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.auth import auth_backend, fastapi_users
from app.models import Base
from app.database import create_db_and_tables, get_async_session
from app.routers import players, matches, register
from app.schemas import UserCreate, UserRead, UserUpdate


# Load Frontend URL
load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(
    title="Volleyball Tracker API",
    description="API for tracking volleyball games and player statistics",
    version="1.0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt", tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix='/auth', tags=["auth"]
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix='/auth', tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix='/auth', tags=["auth"]
)

# Add custom register router
app.include_router(register.router)

# Include routers
app.include_router(players.router)
app.include_router(matches.router)


@app.get("/")
def root():
    return {
        "message": "Volleyball Tracker API",
        "version": "1.0.1",
        "docs": "/docs" 
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
