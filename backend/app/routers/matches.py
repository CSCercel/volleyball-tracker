from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import random

from app.database import get_db
from app.models import Player, PlayerStats, Match, MatchPlayer
from app.schemas import MatchType, MatchCreate, MatchResponse, MatchResultRequest, TeamColor, PlayerBase


router = APIRouter(prefix="/matches", tags=["matches"])



def build_match_response(match: Match) -> MatchResponse:
    """Helper to build MatchResponse from Match model"""
    blue_team_players = [
        PlayerBase(id=mp.player.id, name=mp.player.name) 
        for mp in match.players if mp.color == TeamColor.blue
    ]
    red_team_players = [
        PlayerBase(id=mp.player.id, name=mp.player.name) 
        for mp in match.players if mp.color == TeamColor.red
    ]
    
    return MatchResponse(
        id=match.id,
        match_type=match.match_type,
        season=match.season,
        blue_team=blue_team_players,
        red_team=red_team_players,
        blue_score=match.blue_score,
        red_score=match.red_score,
        created_at=match.created_at,
        updated_at=match.updated_at
    )


@router.post("/draft", response_model=MatchResponse)
def create_match(request: MatchCreate, session: Session = Depends(get_db)):
    # Validate teams have players
    if not request.blue_team or not request.red_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both blue_team and red_team must have at least one player"
        )
    
    # Get all unique player names
    all_player_names = set(request.blue_team + request.red_team)
    
    # Check for duplicates (player on both teams)
    if len(all_player_names) != len(request.blue_team) + len(request.red_team):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Players cannot be on both teams"
        )
    
    # Get all players from database
    players = session.query(Player).filter(Player.name.in_(all_player_names)).all()
    
    if len(players) != len(all_player_names):
        found_names = {p.name for p in players}
        missing = set(all_player_names) - found_names
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Players not found: {list(missing)}"
        )
    
    # Create player lookup
    player_lookup = {p.name: p for p in players}
    
    # Create match (as a draft)
    new_match = Match(
        match_type=request.match_type,
        season=datetime.utcnow().year,
        blue_score=None,
        red_score=None
    )
    session.add(new_match)
    session.flush()  # Get the match ID
    
    # Add blue team players
    for player_name in request.blue_team:
        match_player = MatchPlayer(
            match_id=new_match.id,
            player_id=player_lookup[player_name].id,
            color=TeamColor.blue
        )
        session.add(match_player)
    
    # Add red team players
    for player_name in request.red_team:
        match_player = MatchPlayer(
            match_id=new_match.id,
            player_id=player_lookup[player_name].id,
            color=TeamColor.red
        )
        session.add(match_player)
    
    session.commit()
    session.refresh(new_match)
    
    return build_match_response(new_match)


@router.put("/{match_id}/results", response_model=MatchResponse)
def submit_match_results(match_id: UUID, results: MatchResultRequest, session: Session = Depends(get_db)):
    # Get the match
    match = session.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    # Check if results already submitted
    if match.blue_score is not None or match.red_score is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match results already submitted"
        )
    
    # Update match scores
    match.blue_score = results.blue_score
    match.red_score = results.red_score
    
    # Determine winner
    winner = TeamColor.blue if results.blue_score > results.red_score else TeamColor.red
    
    # Calculate if overtime
    ot_threshold = 24 if match.match_type == MatchType.indoor else 21
    is_overtime = results.blue_score >= ot_threshold and results.red_score >= ot_threshold
    
    # Update stats for all players in the match
    for match_player in match.players:
        player_won = (match_player.color == winner)
        
        update_player_stats(
            session=session,
            player_id=match_player.player_id,
            match_type=match.match_type,
            season=match.season,
            won=player_won,
            is_overtime=is_overtime
        )
    
    session.commit()
    session.refresh(match)
    
    return build_match_response(match)


def update_player_stats(
    session: Session,
    player_id: int,
    match_type: MatchType,
    season: int,
    won: bool,
    is_overtime: bool
):
    # Try to get existing stats
    stats = session.query(PlayerStats).filter(
        PlayerStats.player_id == player_id,
        PlayerStats.match_type == match_type,
        PlayerStats.season == season
    ).first()
    
    # Update stats based on result
    if won:
        stats.wins += 1
    elif is_overtime:
        stats.otl += 1  # Lost in overtime
    else:
        stats.losses += 1  # Regular loss


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: UUID, session: Session = Depends(get_db)):
    match = session.query(Match).filter(Match.id == match_id).first()
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    return build_match_response(match)


@router.get("/", response_model=List[MatchResponse])
def list_matches(
    status: str = "all",
    session: Session = Depends(get_db)
):
    query = session.query(Match)
    
    if status == "draft":
        query = query.filter(Match.blue_score == None)
    elif status == "completed":
        query = query.filter(Match.blue_score != None)
    
    matches = query.order_by(Match.created_at.desc()).all()
    
    return [build_match_response(match) for match in matches]
