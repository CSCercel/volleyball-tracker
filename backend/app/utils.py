from typing import List
import plotly.graph_objects as go
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


def plot_empty_court() -> go.Figure:
    court_width = 9
    court_length = 18
    
    fig = go.Figure()

    # 1. Add Court Boundary (Closed loop)
    fig.add_trace(go.Scatter(
        x=[0, court_width, court_width, 0, 0],
        y=[0, 0, court_length, court_length, 0],
        mode='lines',
        line=dict(color='darkred', width=4),
        name='Boundary'
    ))

    # 2. Centerline
    fig.add_trace(go.Scatter(
        x=[0, court_width],
        y=[court_length / 2, court_length / 2],
        mode='lines',
        line=dict(color='black', width=3, dash='dash'),
        name='Center Line'
    ))

    # 3. Attack Lines (3 meters from center)
    # Blue Team (Bottom)
    fig.add_trace(go.Scatter(
        x=[0, court_width],
        y=[(court_length / 2) - 3, (court_length / 2) - 3],
        mode='lines',
        line=dict(color='darkred', width=2, dash='dash'),
        opacity=0.5,
        name='Attack Line (Blue Team)'
    ))
    
    # Red Team Side (Top)
    fig.add_trace(go.Scatter(
        x=[0, court_width],
        y=[(court_length / 2) + 3, (court_length / 2) + 3],
        mode='lines',
        line=dict(color='darkred', width=2, dash='dash'),
        opacity=0.5,
        name='Attack Line (Red Team)'
    ))

    # 4. Styling the Layout
    fig.update_layout(
        plot_bgcolor='bisque',
        paper_bgcolor='bisque',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, court_width + 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, court_length + 1]),
        width=500,
        height=800,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    return fig


def plot_volleyball_court(blue_team: List[str], red_team: List[str]):

