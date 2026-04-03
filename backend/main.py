from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from app.core.auth import auth_backend, fastapi_users
from app.core.database import Base
from app.core.database import create_db_and_tables, get_async_session
from app.routers import players, matches, register
from app.models.schemas import UserCreate, UserRead, UserUpdate

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(
    title="Volleyball Tracker API",
    description="API for tracking volleyball games and player statistics",
    version="1.1.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
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


@app.get("/health")
def health_check():
    return {"status": "healthy"}
