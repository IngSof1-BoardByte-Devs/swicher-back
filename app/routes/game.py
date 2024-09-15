"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""
from fastapi import APIRouter
from app.schemas.game import GameOut
from app.database.models import Game
from pony.orm import db_session, select

router = APIRouter()


@router.get("/get_games", response_model=list[GameOut])
async def get_games():
    """
    Obtiene los juegos que no han comenzado.
    Returns:
        list[GameOut]: Lista de juegos que no han comenzado.
    """
    with db_session():
        games = select(g for g in Game if g.started == False)[:]
        games = [GameOut(id=g.id, name=g.name, 
                        players=[p.username for p in g.players]) for g in games]
    return games
