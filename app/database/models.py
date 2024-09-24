from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    players = relationship("Player", back_populates="game", foreign_keys='Player.game_id')  # Relación con players, usando game_id como clave foránea
    started = Column(Boolean, default=False)
    turn = Column(Integer, default=0)    
    host = relationship("Player", uselist=False, back_populates="host_game", foreign_keys='Player.host_game_id')    # Relación con host, usando host_game_id como clave foránea

class Player(Base):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    username = Column(String)   
    game_id = Column(Integer, ForeignKey('games.id'))   # Clave foránea a la tabla Game para la relación general (game_id)
    game = relationship("Game", back_populates="players", foreign_keys=[game_id])    
    host_game_id = Column(Integer, ForeignKey('games.id'))  # Clave foránea para la relación host (host_game_id)
    host_game = relationship("Game", back_populates="host", foreign_keys=[host_game_id])
    turn = Column(Integer, default=0)
