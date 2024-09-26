from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    players = relationship("Player", back_populates="game", foreign_keys='Player.game_id')  # Relación con players, usando game_id como clave foránea
    started = Column(Boolean, default=False)
    turn = Column(Integer, default=0)    
    host = relationship("Player", uselist=False, back_populates="host_game", foreign_keys='Player.host_game_id')    # Relación con host, usando host_game_id como clave foránea
        # tablero de enteros de 6x6
    board = ARRAY(ARRAY(Integer))

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    username = Column(String)   
    game_id = Column(Integer, ForeignKey('games.id'))   # Clave foránea a la tabla Game para la relación general (game_id)
    game = relationship("Game", back_populates="players", foreign_keys=[game_id])    
    host_game_id = Column(Integer, ForeignKey('games.id'))  # Clave foránea para la relación host (host_game_id)
    host_game = relationship("Game", back_populates="host", foreign_keys=[host_game_id])
    turn = Column(Integer, default=0)
    movements = relationship("Movement", back_populates="player", foreign_keys='Movement.player_id')
    figures = relationship("Figure", back_populates="player", foreign_keys='Figure.player_id')

class Movement(Base):
    __tablename__ = 'movements'
    # Atributos de los movimientos
    id = Column(Integer, primary_key=True)
    type = Column(String)
    description = Column(String)
    # Relación con player y game
    player_id = Column(Integer, ForeignKey('players.id'))
    player = relationship("Player", back_populates="movements", foreign_keys=[player_id])
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship("Game", back_populates="movements", foreign_keys=[game_id])
    
class Figure(Base):
    __tablename__ = 'figures'
    # Atributos de las figuras
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    # Relación con player y game
    player_id = Column(Integer, ForeignKey('players.id'))
    player = relationship("Player", back_populates="figures", foreign_keys=[player_id])
    game_id = Column(Integer, ForeignKey('games.id'))
    game = relationship("Game", back_populates="figures", foreign_keys=[game_id])
