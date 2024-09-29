"""
Los archivos de schemas se utilizan para definir los esquemas Pydantic. Siven para crear validaciones 
y manejar los datos que se envían y reciben en las peticiones HTTP.
"""

from pydantic import BaseModel
from .player import PlayerOut
from typing import List

class GameOut(BaseModel):
    id: int
    name: str
    num_players: int

class SingleGameOut(BaseModel):
    id: int
    name: str
    started: bool
    turn: int
    bloqued_color: int | None
    players: List[PlayerOut]

class CreateGame(BaseModel):
    player_name: str
    game_name: str

class LeaveStartGame(BaseModel):
    player_id: int
    game_id: int

class GameCreateResponse(BaseModel):
    status: str
    game_id: int

class JoinGame(BaseModel):
    game_id: int
    player_name: str

class StartGame(BaseModel):
    player_id: int
    game_id: int
      
class GameLeaveCreateResponse(BaseModel):
    player_id: int
    game_id: int