from sqlalchemy import (
        Column, Integer, Float, String, Boolean, 
        DateTime, ForeignKey, UniqueConstraint
)
import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from fastapi_users.db import SQLAlchemyBaseUserTable

from sqlalchemy.types import MatchType
from app.database import Base
from app.schemas import MatchType, TeamColor


class User(SQLAlchemyBaseUserTable[uuid.UUID], Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    stats = relationship("PlayerStats", back_populates="player", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PlayerStats(Base):
    __tablename__ = "player_stats"

    __table_args__ = (
       UniqueConstraint('player_id', 'match_type', 'season', name='unique_player_stats'),
   )

    id = Column(Integer, primary_key=True)

    player_id = Column(ForeignKey("players.id"))
    match_type = Column(SQLEnum(MatchType)) 
    season = Column(Integer, default=datetime.utcnow().year)

    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    otl = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    player = relationship("Player", back_populates="stats")


class Match(Base):
    __tablename__ = "matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_type = Column(SQLEnum(MatchType))
    season = Column(Integer, default=datetime.utcnow().year)
    blue_score = Column(Integer, nullable=True, default=None)
    red_score = Column(Integer, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    players = relationship("MatchPlayer", back_populates="match", cascade="all, delete-orphan")


class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True)
    match_id = Column(ForeignKey("matches.id"))
    player_id = Column(ForeignKey("players.id"))
    color = Column(SQLEnum(TeamColor))

    match = relationship("Match", back_populates="players")
    player = relationship("Player")
