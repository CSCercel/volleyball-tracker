from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth_backend, fastapi_users
from app.schemas import UserCreate, UserRead
from app.models import Base
from app.database import engine, Base
from app.routers import players, matches


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Volleyball Tracker API",
    description="API for tracking volleyball games and player statistics",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth routes
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)


# Include routers
app.include_router(players.router)
app.include_router(matches.router)


@app.get("/")
def root():
    return {
        "message": "Volleyball Tracker API",
        "version": "0.1.0",
        "docs": "/docs" 
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
