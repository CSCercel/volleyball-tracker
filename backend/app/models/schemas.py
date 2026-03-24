import uuid
from pydantic import UUID4, BaseModel, computed_field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from fastapi_users import schemas


class UserCreate(schemas.BaseUserCreate):
    pass


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    registration_code: str


class MatchType(str, Enum):
    indoor = "indoor"
    beach = "beach"


class TeamColor(str, Enum):
    blue = "blue"
    red = "red"


class PlayerBase(BaseModel):
    id: int
    name: str
    efficiency: float

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
    streak: int
    longest_streak: int
    scored: int
    conceded: int

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

    @computed_field
    @property
    def avg_points(self) -> float:
        total = self.played
        if total == 0:
            return 0
        else:
            return self.points / total

    @computed_field
    @property
    def efficiency(self) -> float:
        conceded = self.conceded
        if conceded == 0:
            return 0
        else:
            return self.scored / conceded

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
        
        ot_threshold = 24 if self.match_type == MatchType.indoor else 20
        return self.blue_score >= ot_threshold and self.red_score >= ot_threshold
   
    @computed_field
    @property
    def blue_mvp(self) -> str:
        best_player = self.blue_team[0].name
        best_player_eff = self.blue_team[0].efficiency
        for p in self.blue_team:
            if p.efficiency > best_player_eff:
                best_player = p.name
                best_player_eff = p.efficiency

        return best_player

    @computed_field
    @property
    def red_mvp(self) -> str:
        best_player = self.red_team[0].name
        best_player_eff = self.red_team[0].efficiency
        for p in self.red_team:
            if p.efficiency > best_player_eff:
                best_player = p.name
                best_player_eff = p.efficiency

        return best_player
    
    @computed_field
    @property
    def blue_odds(self) -> float:
        blue_eff, red_eff = 0, 0
        for p in self.blue_team:
            blue_eff += p.efficiency
        for p in self.red_team:
            red_eff += p.efficiency
        
        if blue_eff + red_eff == 0:
            return 0.5
        else:
            return blue_eff / (blue_eff + red_eff)

    @computed_field
    @property
    def red_odds(self) -> float:
        return 1 - self.blue_odds

    class Config:
        from_attributes = True
