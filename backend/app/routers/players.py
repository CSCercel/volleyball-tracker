from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.database import get_async_session
from app.auth import current_active_user
from app.models import Player, PlayerStats, User
from app.schemas import MatchType, PlayerCreate, PlayerResponse


router = APIRouter(prefix="/players", tags=["players"])


@router.post("/create", response_model=PlayerResponse)
async def create_player(
    player: PlayerCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    response = await session.execute(
        select(Player).filter(Player.name == player.name)
    )
    existing_player = response.scalar_one_or_none()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player with this name already exists"
        )

    # Create new player
    new_player = Player(name=player.name)
    session.add(new_player)
    await session.flush()

    # Initialize stats for both match types
    for match_type in MatchType:
        stats = PlayerStats(
            player_id=new_player.id,
            match_type=match_type,
            season=datetime.utcnow().year,
            wins=0,
            losses=0,
            otl=0,
            streak=0,
            longest_streak=0
        )
        session.add(stats)

    await session.commit()

    result = await session.execute(
        select(Player).options(selectinload(Player.stats)).filter(Player.id == new_player.id)
    )

    new_player_complete = result.scalar_one_or_none()

    return new_player_complete


@router.get("/", response_model=List[PlayerResponse])
async def list_players(session: AsyncSession = Depends(get_async_session)):
    response = await session.execute(
        select(Player).options(selectinload(Player.stats)).order_by(Player.name)
    )

    players = [row[0] for row in response.all()]

    return players


@router.get("/{name}", response_model=PlayerResponse)
async def get_player(name: str, session: AsyncSession = Depends(get_async_session)):
    response = await session.execute(
        select(Player).options(selectinload(Player.stats)).where(Player.name == name)
    )

    player = response.scalar_one_or_none()

    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        ) 
    return player
