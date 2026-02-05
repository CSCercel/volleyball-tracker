from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class MatchTeam(str, enum.Enum):
    BLUE = "blue"
    RED = "red"

class MatchType(str, enum.Enum):
    INDOOR = "indoor"
    BEACH = "beach"


class MatchOutcome(str, enum.Enum):
    WIN = "win"
    OVERTIME_LOSS = "overtime_loss"
    LOSS = "loss"

# Association table for many-to-many relationship between players and matches
match_players = Table(
    'match_players',
    Base.metadata,
    Column('match_id', Integer, ForeignKey('matches.id'), primary_key=True),
    Column('player_id', Integer, ForeignKey('players.id'), primary_key=True),
    Column('team', Enum(MatchTeam), nullable=False), 
    Column('outcome', Enum(MatchOutcome), nullable=False) 
)

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    
    # Statistics (these will be calculated from matches)
    total_points = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    overtime_losses = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to matches (many-to-many through match_players table)
    matches = relationship(
        "Match",
        secondary=match_players,
        back_populates="players"
    )

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    match_type = Column(Enum(MatchType), nullable=False)
    match_date = Column(DateTime, default=datetime.utcnow)
    blue_score = Column(Integer, nullable=False)
    red_score = Column(Integer, nullable=False)
    is_overtime = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to players (many-to-many through match_players table)
    players = relationship(
        "Player",
        secondary=match_players,
        back_populates="matches"
    )
    
    def calculate_outcomes(self):
        """
        Helper method to determine the outcome for each team.
        Returns a tuple of (blue_outcome, red_outcome)
        """
        if self.blue_score > self.red_score:
            blue_outcome = MatchOutcome.WIN
            red_outcome = MatchOutcome.OVERTIME_LOSS if self.is_overtime else MatchOutcome.LOSS
        else:
            red_outcome = MatchOutcome.WIN
            blue_outcome = MatchOutcome.OVERTIME_LOSS if self.is_overtime else MatchOutcome.LOSS
        
        return blue_outcome, red_outcome
