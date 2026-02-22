from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional 
from uuid import UUID
from datetime import date

from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.auth import current_active_user
from app.models import Player, PlayerStats, Match, MatchPlayer, User
from app.schemas import MatchCreate, MatchResponse, MatchResultRequest, PlayerBase, MatchType, TeamColor
from app.utils import build_match_response, update_player_stats


router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/create", response_model=MatchResponse)
async def create_match(
    request: MatchCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
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
    response = await session.execute(
            select(Player).options(selectinload(Player.stats)).filter(Player.name.in_(all_player_names))
    )

    players = [row[0] for row in response.all()]
    
    if len(players) != len(all_player_names):
        found_names = {p.name for p in players}
        missing = set(all_player_names) - found_names
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Players not found: {list(missing)}"
        )
    
    # Create player lookup
    player_lookup = {p.name: p for p in players}
    
    # Create match (no scores yet - this is a draft)
    new_match = Match(
        match_type=request.match_type,
        blue_score=None,
        red_score=None
    )
    session.add(new_match)
    await session.flush()  # Get the match ID
    
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

    await session.commit()
    await session.refresh(new_match)

    result = await session.execute(
        select(Match)
        .options(
            selectinload(Match.players)
            .selectinload(MatchPlayer.player)
            .selectinload(Player.stats)
        )
        .filter(Match.id == new_match.id)
    )

    new_match_complete = result.scalar_one_or_none()

    return build_match_response(new_match_complete)


@router.put("/{match_id}/results", response_model=MatchResponse)
async def submit_match_results(
    match_id: UUID,
    results: MatchResultRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Get the match
    response = await session.execute(
        select(Match).options(selectinload(Match.players)).filter(Match.id == match_id)
    )

    match = response.scalar_one_or_none()

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
    
    # Determine winner (calculate here, not from match.winner)
    winner = TeamColor.blue if results.blue_score > results.red_score else TeamColor.red
    
    # Calculate if overtime
    ot_threshold = 24 if match.match_type == MatchType.indoor else 20
    is_overtime = results.blue_score >= ot_threshold and results.red_score >= ot_threshold
    
    # Get all match players
    players_response = await session.execute(
        select(MatchPlayer).filter(MatchPlayer.match_id == match_id)
    )

    match_players = [row[0] for row in players_response.all()]
    
    # Update stats for all players in the match
    for match_player in match_players:
        player_won = (match_player.color == winner) 
        
        await update_player_stats(
            session=session,
            player_id=match_player.player_id,
            match_type=match.match_type,
            season=match.season,
            won=player_won,
            is_overtime=is_overtime
        )
    
    await session.commit()

    result = await session.execute(
        select(Match)
        .options(
            selectinload(Match.players)
                .selectinload(MatchPlayer.player)
                .selectinload(Player.stats)
        )
        .filter(Match.id == match.id)
    )

    new_match = result.scalar_one_or_none()
    return build_match_response(new_match)


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: UUID, session: AsyncSession = Depends(get_async_session)):
    response = await session.execute(
        select(Match)
        .options(
            selectinload(Match.players)
                .selectinload(MatchPlayer.player)
                .selectinload(Player.stats)
        )
        .filter(Match.id == match_id)
    )
    
    match = response.scalar_one_or_none()

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )
    
    return build_match_response(match)


@router.get("/", response_model=List[MatchResponse])
async def list_matches(
    status: str = "all",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    session: AsyncSession = Depends(get_async_session)
):
    query = (
        select(Match)
        .options(
            selectinload(Match.players)
                .selectinload(MatchPlayer.player)
                .selectinload(Player.stats)
        )
    )
    
    if status == "draft":
        query = query.filter(Match.blue_score == None)
    elif status == "completed":
        query = query.filter(Match.blue_score != None)

    if start_date:
        query = query.filter(Match.created_at >= start_date)
    if end_date:
        query = query.filter(Match.created_at <= end_date)

    query = query.order_by(Match.created_at.desc())

    response = await session.execute(query)

    matches = [row[0] for row in response.all()]
    
    return [build_match_response(match) for match in matches]


@router.delete("/{match_id}")
async def delete_match(
    match_id: UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    response = await session.execute(
        select(Match)
        .options(
            selectinload(Match.players)
                .selectinload(MatchPlayer.player)
                .selectinload(Player.stats)
        )
        .filter(Match.id == match_id)
    )

    match = response.scalar_one_or_none()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )

    if match.blue_score != None and match.red_score != None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Match has already been registered."
        )

    await session.delete(match)
    await session.commit()
