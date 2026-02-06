from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_async_session
from app.models import Player
from app.schemas import PlayerCreate, PlayerResponse


router = APIRouter(
    prefix="/players",  
    tags=["players"]
)


@router.post("/create", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
        player: PlayerCreate, 
        session: AsyncSession = Depends(get_async_session)
):
    new_player = Player(name=player.name)

    # Write to database
    session.add(new_player)
    await session.commit()
    await session.refresh(new_player)

    return new_player

@router.get("/roster", response_model=List[PlayerResponse])
async def list_players(session: AsyncSession = Depends(get_async_session)):
    response = await session.execute(select(Player).order_by(Player.name))

    players = [row[0] for row in response.all()]

    return players

@router.get("/roster/{name}", response_model=PlayerResponse)
async def get_player(
        name: str,
        session: AsyncSession = Depends(get_async_session)
):
    response = await session.execute(select(Player).where(Player.name == name))
    
    return response.scalar_one_or_none()
