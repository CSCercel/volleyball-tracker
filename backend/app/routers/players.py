from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_async_session
from app.models import Player, PlayerStats
from app.schemas import MatchType, PlayerCreate, PlayerResponse


router = APIRouter(
    prefix="/players",  
    tags=["players"]
)


@router.post("/create")
async def create_player(
        player: PlayerCreate, 
        session: AsyncSession = Depends(get_async_session)
) -> PlayerResponse:
    new_player = Player(name=player.name)

    new_player.stats = [
        PlayerStats(match_type=MatchType.indoor),
        PlayerStats(match_type=MatchType.beach)
    ]

    # Write to database
    session.add(new_player)
    await session.commit()
    await session.refresh(new_player)

    return new_player

@router.get("/roster")
async def list_players(
        session: AsyncSession = Depends(get_async_session)
) -> List[PlayerResponse]:
    response = await session.execute(select(Player).order_by(Player.name))

    players = [row[0] for row in response.all()]

    return players

@router.get("/roster/{name}")
async def get_player(
        name: str,
        session: AsyncSession = Depends(get_async_session)
) -> PlayerResponse:
    response = await session.execute(select(Player).where(Player.name == name))
    
    return response.scalar_one_or_none()
