from uuid import UUID
from pydantic import UUID4, BaseModel, computed_field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MatchType(str, Enum):
    indoor = "indoor"
    beach = "beach"


class TeamColor(str, Enum):
    blue = "blue"
    red = "red"


class PlayerBase(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PlayerCreate(BaseModel):
    name: str


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


class MatchCreate(BaseModel):
    match_type: MatchType
    blue_team: List[str]
    red_team: List[str]


class MatchResultRequest(BaseModel):
    blue_score: int
    red_score: int


class MatchResponse(BaseModel):
    id: UUID4
    match_type: MatchType
    season: int
    blue_team: List[PlayerBase]
    red_team: List[PlayerBase]
    blue_score: Optional[int]
    red_score: Optional[int]
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def status(self) -> str:
        if self.blue_score is None or self.red_score is None:
            return "draft"
        return "completed"
    
    @computed_field
    @property
    def winner(self) -> Optional[str]:
        if self.blue_score is None or self.red_score is None:
            return None
        elif self.blue_score > self.red_score:
            return TeamColor.blue.value
        else:
            return TeamColor.red.value
    
    @computed_field
    @property
    def is_overtime(self) -> bool:
        if self.blue_score is None or self.red_score is None:
            return False
        
        ot_threshold = 24 if self.match_type == MatchType.indoor else 21
        return self.blue_score >= ot_threshold and self.red_score >= ot_threshold
    
    class Config:
        from_attributes = True
