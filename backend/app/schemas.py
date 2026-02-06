from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class PlayerCreate(BaseModel):
    name: str

class PlayerResponse(BaseModel):
    id: int
    name: str

    # Stats
    indoor_wins: int
    indoor_losses: int
    indoor_otl: int

    beach_wins: int
    beach_losses: int
    beach_otl: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PlayerUpdate(BaseModel):
    name: Optional[str]
