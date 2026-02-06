from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import Base, Player
from app.database import create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.routers import players


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    title="Volleyball Tracker API",
    description="API for tracking volleyball games and player statistics",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Volleyball Tracker API",
        "version": "1.0.0",
        "docs": "/docs" 
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(players.router)
# app.include_router(matches.router)
