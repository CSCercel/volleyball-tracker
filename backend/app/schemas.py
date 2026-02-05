from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from app.models import MatchType, MatchOutcome


class PlayerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Player name")

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)

class PlayerResponse(PlayerBase):
    id: int
    total_points: int
    wins: int
    losses: int
    overtime_losses: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MatchPlayerInput(BaseModel):
    player_id: int
    team: Literal["blue", "red"] = Field(..., description="Blue team or Red team")

class MatchCreate(BaseModel):
    match_type: MatchType
    blue_score: int = Field(..., ge=0, description="Blue Team score")
    red_score: int = Field(..., ge=0, description="Red Team score")
    is_overtime: bool = Field(default=False, description="Was this an overtime match?")
    players: List[MatchPlayerInput] = Field(..., min_items=2, description="List of players and their teams")
    
    class Config:
        # Example for API documentation
        json_schema_extra = {
            "example": {
                "match_type": "indoor",
                "blue_score": 25,
                "red_score": 23,
                "is_overtime": True,
                "players": [
                    {"player_id": 1, "team": "blue"},
                    {"player_id": 2, "team": "blue"},
                    {"player_id": 3, "team": "red"},
                    {"player_id": 4, "team": "red"}
                ]
            }
        }

class MatchPlayerResponse(BaseModel):
    player_id: int
    player_name: str
    team: Literal["blue", "red"]
    outcome: MatchOutcome
    
    class Config:
        from_attributes = True

class MatchResponse(BaseModel):
    id: int
    match_type: MatchType
    match_date: datetime
    blue_score: int
    red_score: int
    is_overtime: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchDetailResponse(MatchResponse):
    players: List[MatchPlayerResponse]

class TeamDraftRequest(BaseModel):
    player_ids: List[int] = Field(..., min_items=2, description="List of player IDs to draft into teams")
    random: bool = Field(default=False, description="If True, randomly assign teams. If False, manual assignment expected.")

class TeamDraftResponse(BaseModel):
    blue: List[PlayerResponse]
    red: List[PlayerResponse]


class PlayerStats(BaseModel):
    player: PlayerResponse
    total_matches: int
    win_rate: float = Field(..., description="Percentage of matches won (0-100)")
    
    class Config:
        from_attributes = True
