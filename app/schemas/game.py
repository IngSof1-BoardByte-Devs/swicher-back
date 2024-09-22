"""
Los archivos de schemas se utilizan para definir los esquemas Pydantic. Siven para crear validaciones 
y manejar los datos que se envían y reciben en las peticiones HTTP.
"""

from pydantic import BaseModel

class GameOut(BaseModel):
    id: int
    name: str
    players: list

class CreateGame(BaseModel):
    name: str
    host: list

class LeaveStartGame(BaseModel):
    player_id: int
    game_id: int

class PlayerTest(BaseModel):
    id: int
    username: str
    game: int
    host_game: int

class GameTest(BaseModel):
    id: int
    name: str
    players: list