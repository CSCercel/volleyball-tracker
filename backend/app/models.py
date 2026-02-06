from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime

from sqlalchemy.types import MatchType
from app.database import Base
from app.schemas import MatchType, TeamColor


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    stats = relationship("PlayerStats", back_populates="player", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PlayerStats(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True)

    player_id = Column(ForeignKey("players.id"))
    match_type = Column(SAEnum(MatchType)) 

    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    otl = Column(Integer, default=0)

    player = relationship("Player", back_populates="stats")


class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_type = Column(SAEnum(MatchType)) 

    blue_score = Column(Integer, nullable=True)
    red_score = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    teams = relationship("MatchTeam", back_populates="match")

    winner = Column(String)
    is_overtime = Column(Boolean)

class MatchTeam(Base):
    __tablename__ = "match_teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    match_id = Column(ForeignKey("matches.id"))
    color = Column(SAEnum(TeamColor))

    match = relationship("Match", back_populates="teams")
    players = relationship("MatchPlayer", back_populates="team")

class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True)

    team_id = Column(ForeignKey("match_teams.id"))
    player_id = Column(ForeignKey("players.id"))

    team = relationship("MatchTeam", back_populates="players")
    player = relationship("Player")
