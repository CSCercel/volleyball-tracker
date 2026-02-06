from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
    response = await session.execute(select(Player).filter(Player.name == player.name))
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
            wins=0,
            losses=0,
            otl=0
        )
        session.add(stats)

    await session.commit()
    
    result = await session.execute(
        select(Player).options(selectinload(Player.stats)).filter(Player.id == new_player.id)
    )

    new_player = result.scalar_one_or_none()
    return new_player

@router.get("/roster")
async def list_players(
        session: AsyncSession = Depends(get_async_session)
) -> List[PlayerResponse]:
    response = await session.execute(
        select(Player).options(selectinload(Player.stats)).order_by(Player.name)
    )

    players = [row[0] for row in response.all()]

    return players

@router.get("/roster/{name}")
async def get_player(
        name: str,
        session: AsyncSession = Depends(get_async_session)
) -> PlayerResponse:
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

# @router.patch("/{player_id}", response_model=PlayerResponse)
# async def update_player(
#     player_id: int,
#     player_update: PlayerUpdate,
#     db: AsyncSession = Depends(get_async_session)
# ):
#     """Update player information"""
#     result = await db.execute(select(Player).filter(Player.id == player_id))
#     player = result.scalar_one_or_none()
#     if not player:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Player not found"
#         )
#
#     # Check if new name already exists
#     if player_update.name:
#         result = await db.execute(
#             select(Player).filter(
#                 Player.name == player_update.name,
#                 Player.id != player_id
#             )
#         )
#         existing = result.scalar_one_or_none()
#         if existing:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Player with this name already exists"
#             )
#         player.name = player_update.name
#
#     await db.commit()
#     await db.refresh(player)
#     return player

@router.delete("/roster/{player_id}")
async def delete_player(
        name: str, 
        session: AsyncSession = Depends(get_async_session)
):
    response = await session.execute(
        select(Player).options(selectinload(Player.stats)).where(Player.name == name)
    )

    player = response.scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    await session.delete(player)
    await session.commit()
