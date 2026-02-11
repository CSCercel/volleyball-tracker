from pydantic import UUID4, BaseModel, computed_field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import random


class MatchType(str, Enum):
    indoor = "indoor"
    beach = "beach"

class TeamColor(str, Enum):
    blue = "blue"
    red = "red"

class PlayerBase(BaseModel):
    name: str

class PlayerCreate(PlayerBase):
    pass

class PlayerStatsResponse(BaseModel):
    match_type: MatchType
    season: int
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

class TeamCreate(BaseModel):
    roster: List[str]

class TeamResponse(BaseModel):
    blue_team: List[str]
    red_team: List[str]

class MatchCreate(BaseModel):
    id: UUID4
    match_type: MatchType

class MatchResponse(BaseModel):
    id: UUID4
    match_type: MatchType
    blue_score: int
    red_score: int
    created_at: datetime
    updated_at: datetime

    teams: TeamResponse

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
        if self.match_type == MatchType.indoor:
            ot_score = 24
        else:
            ot_score = 21
        return self.blue_score >= ot_score and self.red_score >= ot_score

    class Config:
        from_attributes = True
