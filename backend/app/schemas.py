from threading import main_thread
from pydantic import UUID4, BaseModel, computed_field
from typing import Optional, List, Literal
from datetime import datetime
import enum
import random


class MatchType(str, enum.Enum):
    indoor = "indoor"
    beach = "beach"

class TeamColor(str, enum.Enum):
    blue = "blue"
    red = "red"

class PlayerCreate(BaseModel):
    name: str

class PlayerStatsResponse(BaseModel):
    match_type: MatchType
    wins: int
    losses: int
    otl: int

    @computed_field
    @property
    def played(self) -> int:
        return self.wins + self.losses + self.otl

    @computed_field
    @property
    def points(self) -> int:
        return self.wins * 2 + self.otl

    @computed_field
    @property
    def winrate(self) -> float:
        total = self.played
        if total == 0:
            return 0
        else:
            return self.wins / total

    class Config:
        from_attributes = True

class PlayerResponse(BaseModel):
    id: int
    name: str
    stats: List[PlayerStatsResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PlayerUpdate(BaseModel):
    name: Optional[str]

class PlayerMatchResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class MatchTeamResponse(BaseModel):
    color: TeamColor
    players: list[PlayerMatchResponse]

    class Config:
        from_attributes = True

class MatchResponse(BaseModel):
    id: UUID4
    match_type: MatchType
    blue_score: int
    red_score: int
    created_at: datetime
    updated_at: datetime

    teams: list[MatchTeamResponse]

    @computed_field
    @property
    def winner(self) -> str:
        if self.blue_score + self.red_score == 0:
            return "draft"

        elif self.blue_score > self.red_score:
            return TeamColor.blue
        else:
            return TeamColor.red

    @computed_field
    @property
    def is_overtime(self) -> bool:
        return self.blue_score >= 24 and self.red_score >= 24

    class Config:
        from_attributes = True
