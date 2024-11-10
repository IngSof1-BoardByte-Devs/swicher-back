from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import CheckConstraint
from app.utils.enums import MovementType, MovementStatus, FigureType, FigureStatus
import json

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    name = Column(String)
    started = Column(Boolean, default=False)
    turn = Column(Integer, default=0)
    bloqued_color = Column(Integer, default=None)
    board = Column(String)
    
    # Relaciones
    players = relationship("Player", back_populates="game", foreign_keys='Player.game_id')
    host = relationship("Player", uselist=False, back_populates="host_game", foreign_keys='Player.host_game_id')
    movements = relationship("Movement", back_populates="game", cascade="all, delete-orphan")
    figures = relationship("Figure", cascade="all, delete-orphan")
    partial_movements = relationship("PartialMovement", back_populates="game", cascade="all, delete-orphan")

    # Métodos para manejar la matriz del tablero
    @property
    def board_matrix(self):
        return json.loads(self.board)
    
    @board_matrix.setter
    def board_matrix(self, matrix):
        self.board = json.dumps(matrix)

class Player(Base):
    __tablename__ = 'players'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    game_id = Column(Integer, ForeignKey('games.id', ondelete="CASCADE"), nullable=False)
    host_game_id = Column(Integer, ForeignKey('games.id'))
    turn = Column(Integer, default=0)
    conected = Column(Boolean, default=True)
    
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
    partial_movements = relationship("PartialMovement", back_populates="movement", cascade="all, delete-orphan")


class Figure(Base):
    __tablename__ = 'figures'
    
    # Atributos internos
    id = Column(Integer, primary_key=True)
    type = Column(Enum(FigureType))
    status = Column(Enum(FigureStatus), default=FigureStatus.INDECK)
    
    # Relaciones
    player_id = Column(Integer, ForeignKey('players.id'), nullable=True)
    player = relationship("Player", foreign_keys=[player_id], back_populates="figures")
    game_id = Column(Integer, ForeignKey('games.id', ondelete="CASCADE"), nullable=False)
    game = relationship("Game", back_populates="figures")


class PartialMovement(Base):
    __tablename__ = 'partial_movements'

    id = Column(Integer, primary_key=True)
    game_id = Column(Integer, ForeignKey('games.id'))
    movement_id = Column(Integer, ForeignKey('movements.id'))
    x1 = Column(Integer)
    x2 = Column(Integer)
    y1 = Column(Integer)
    y2 = Column(Integer)

    game = relationship("Game", back_populates="partial_movements")
    movement = relationship("Movement", back_populates="partial_movements")