from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import CheckConstraint
from app.utils.enums import *

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    name = Column(String)
    started = Column(Boolean, default=False)
    turn = Column(Integer, default=0)    
    board = Column(ARRAY(Integer), default=None)
    
    # Relaciones
    players = relationship("Player", back_populates="game", foreign_keys='Player.game_id')
    host = relationship("Player", uselist=False, back_populates="host_game", foreign_keys='Player.host_game_id')
    
    __table_args__ = (
        CheckConstraint('array_length(board, 1) = 36', name='check_board_length'),
    )


class Player(Base):
    __tablename__ = 'players'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', ondelete="CASCADE"), nullable=False)
    host_game_id = Column(Integer, ForeignKey('games.id'))
    turn = Column(Integer, default=0)
    
    # Relaciones
    game = relationship("Game", back_populates="players", foreign_keys=[game_id])    
    host_game = relationship("Game", back_populates="host", foreign_keys=[host_game_id])
    movements = relationship("Movement", back_populates="player", foreign_keys='Movement.player_id', lazy="dynamic")
    figures = relationship("Figure", back_populates="player", foreign_keys='Figure.player_id')


class Movement(Base):
    __tablename__ = 'movements'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    type = Column(Enum(MovementType))
    status = Column(Enum(MovementStatus), default=MovementStatus.INDECK)
    
    # Relaciones
    player_id = Column(Integer, ForeignKey('players.id', ondelete='SET NULL'), nullable=True)
    player = relationship("Player", back_populates="movements", foreign_keys=[player_id])
    game_id = Column(Integer, ForeignKey('games.id', ondelete="CASCADE"), nullable=False)
    game = relationship("Game", back_populates="movements", foreign_keys=[game_id])


class Figure(Base):
    __tablename__ = 'figures'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    type = Column(Enum(FigureType))
    status = Column(Enum(FigureStatus), default=FigureStatus.INDECK)
    
    # Relaciones
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player = relationship("Player", back_populates="figures", foreign_keys=[player_id])
    game_id = Column(Integer, ForeignKey('games.id', ondelete="CASCADE"), nullable=False)
    game = relationship("Game", back_populates="figures", foreign_keys=[game_id])