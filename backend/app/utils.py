from sqlalchemy.orm import Session
from app.models import Match, PlayerStats
from app.schemas import PlayerBase, MatchResponse, MatchType, TeamColor


def build_match_response(match: Match) -> MatchResponse:
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
        stats.streak += 1
        
        if stats.streak > stats.longest_streak:
            stats.longest_streak = stats.streak

    elif is_overtime:
        stats.otl += 1
        stats.streak = 0
    else:
        stats.losses += 1
        stats.streak = 0
