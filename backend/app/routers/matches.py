from fastapi import APIRouter, Depends, HTTPException, status
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
