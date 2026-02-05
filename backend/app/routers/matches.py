from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import random

from app.database import get_async_session
from app.models import Player, Match, MatchOutcome, match_players
from app.schemas import (
    MatchCreate, MatchResponse, MatchDetailResponse, MatchPlayerResponse,
    TeamDraftRequest, TeamDraftResponse, PlayerResponse
)

router = APIRouter(
    prefix="/matches",
    tags=["matches"]
)


@router.post("/", response_model=MatchDetailResponse, status_code=status.HTTP_201_CREATED)
def create_match(match: MatchCreate, db: AsyncSession = Depends(get_async_session)):


@router.get("/", response_model=List[MatchResponse])
def list_matches(db: AsyncSession = Depends(get_async_session)):


@router.get("/{match_id}", response_model=MatchDetailResponse)
def get_match(match_id: int, db: AsyncSession = Depends(get_async_session)):


@router.post("/draft-teams", response_model=TeamDraftResponse)
def draft_teams(request: TeamDraftRequest, db: AsyncSession = Depends(get_async_session)):
