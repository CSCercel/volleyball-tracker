from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Stats
    indoor_wins = Column(Integer, default=0)
    indoor_losses = Column(Integer, default=0)
    indoor_otl = Column(Integer, default=0)

    beach_wins = Column(Integer, default=0)
    beach_losses = Column(Integer, default=0)
    beach_otl = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
