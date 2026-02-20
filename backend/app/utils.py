from sqlalchemy.orm import Session
from app.models import Match, MatchPlayer, Player, PlayerStats
from app.schemas import PlayerBase, MatchResponse, MatchType, TeamColor


def get_player_base(player: Player, match_type: MatchType, season: int) -> PlayerBase:
    stats = next(
        (s for s in player.stats if s.match_type == match_type and s.season == season),
        None
    )
    
    points = (stats.wins * 2 + stats.otl) if stats else 0
    
    return PlayerBase(id=player.id, name=player.name, points=points)


def build_match_response(match: Match, session: Session) -> MatchResponse:
    match_players = session.query(MatchPlayer).filter(
        MatchPlayer.match_id == match.id
    ).join(Player).all()
    
    blue_team_players = [
        get_player_base(mp.player, match.match_type, match.season)
        for mp in match_players if mp.color == TeamColor.blue
    ]
    
    red_team_players = [
        get_player_base(mp.player, match.match_type, match.season)
        for mp in match_players if mp.color == TeamColor.red
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
    
    if not stats:
        stats = PlayerStats(
            player_id=player_id,
            match_type=match_type,
            season=season,
            wins=0,
            losses=0,
            otl=0,
            streak=0,
            longest_streak=0
        )
        session.add(stats)

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
