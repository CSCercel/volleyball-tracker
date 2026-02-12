from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
        "version": "0.1.0",
        "docs": "/docs" 
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include routers
app.include_router(players.router)
app.include_router(matches.router)
