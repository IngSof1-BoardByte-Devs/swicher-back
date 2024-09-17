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
