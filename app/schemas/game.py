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
    player_name: str
    game_name: str

class GameCreateResponse(BaseModel):
    status: str
    game_id: int
