from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import Player, PlayerStats
from app.schemas import MatchType, PlayerCreate, PlayerResponse


router = APIRouter(prefix="/players", tags=["players"])


@router.post("/create", response_model=PlayerResponse)
def create_player(player: PlayerCreate, session: Session = Depends(get_db)):
    response = session.query(Player).filter(Player.name == player.name)
    existing_player = response.first()
    if existing_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Player with this name already exists"
        )

    # Create new player
    new_player = Player(name=player.name)

    # Initialize stats for both match types
    for match_type in MatchType:
        stats = PlayerStats(
            player_id=new_player.id,
            match_type=match_type,
            season=datetime.utcnow().year,
            wins=0,
            losses=0,
            otl=0
        )
        new_player.stats.append(stats)
        
    session.add(new_player)
    session.commit()

    # Calculate computed fields
    session.refresh(new_player)

    return new_player

@router.get("/", response_model=List[PlayerResponse])
def list_players( session: Session = Depends(get_db)):
    response = session.query(Player).order_by(Player.name).all()

    return response

@router.get("/{name}", response_model=PlayerResponse)
def get_player( name: str, session: Session = Depends(get_db)):
    response = session.query(Player).where(Player.name == name).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        ) 
    return response

@router.delete("/{player_id}")
def delete_player( name: str, session: Session = Depends(get_db)):
    response = session.query(Player).where(Player.name == name)

    player = response.first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    session.delete(player)
    session.commit()
