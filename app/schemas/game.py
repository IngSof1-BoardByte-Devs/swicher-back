"""
Los archivos de schemas se utilizan para definir los esquemas Pydantic. Siven para crear validaciones 
y manejar los datos que se envían y reciben en las peticiones HTTP.
"""

from pydantic import BaseModel

class GameOut(BaseModel):
    id: int
    name: str
    num_players: int

class CreateGame(BaseModel):
    game_name: str
    player_name: str

class GameCreateResponse(BaseModel):
    status: str
    game_id: int

class JoinGame(BaseModel):
    game_id: int
    player_name: str

class StartGame(BaseModel):
    player_id: int
    game_id: int