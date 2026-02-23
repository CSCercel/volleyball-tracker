from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Match, MatchPlayer, Player, PlayerStats
from app.schemas import PlayerBase, MatchResponse, MatchType, TeamColor


def get_player_base(player: Player, match_type: MatchType, season: int) -> PlayerBase:
    stats = next(
        (s for s in player.stats if s.match_type == match_type and s.season == season),
        None
    )
    
    scored = stats.scored if stats else 0
    conceded = stats.conceded if stats else 0

    if conceded == 0:
        efficiency = 0
    else:
        efficiency = scored / conceded

    return PlayerBase(id=player.id, name=player.name, efficiency=efficiency)


def build_match_response(match: Match) -> MatchResponse:
    
    blue_team_players = [
        get_player_base(mp.player, match.match_type, match.season)
        for mp in match.players if mp.color == TeamColor.blue
    ]
    
    red_team_players = [
        get_player_base(mp.player, match.match_type, match.season)
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


async def update_player_stats(
    session: AsyncSession,
    player_id: int,
    match_type: MatchType,
    season: int,
    won: bool,
    is_overtime: bool,
    scored: int,
    conceded: int
):
    # Try to get existing stats
    response = await session.execute(
                select(PlayerStats).filter(
                    PlayerStats.player_id == player_id,
                    PlayerStats.match_type == match_type,
                    PlayerStats.season == season
                )
    )

    stats = response.scalar_one_or_none()
    
    if not stats:
        stats = PlayerStats(
            player_id=player_id,
            match_type=match_type,
            season=season,
            wins=0,
            losses=0,
            otl=0,
            streak=0,
            longest_streak=0,
            scored=0,
            conceded=0
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

    # Update scored/conceded fields
    stats.scored += scored
    stats.conceded += conceded
