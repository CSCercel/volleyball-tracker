from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_async_session
from app.models import Player
from app.schemas import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerStats


router = APIRouter(
    prefix="/players",  
    tags=["players"]
)


@router.post("/", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerCreate, session: AsyncSession = Depends(get_async_session)):


@router.get("/", response_model=List[PlayerResponse])
async def list_players(session: AsyncSession = Depends(get_async_session)):


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, session: AsyncSession = Depends(get_async_session)):


@router.put("/{player_id}", response_model=PlayerResponse)
async def update_player(
    player_id: int,
    player_update: PlayerUpdate,
    session: AsyncSession = Depends(get_async_session)
):


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int, session: AsyncSession = Depends(get_async_session)):


@router.get("/{player_id}/stats", response_model=PlayerStats)
async def get_player_stats(player_id: int, session: AsyncSession = Depends(get_async_session)):
