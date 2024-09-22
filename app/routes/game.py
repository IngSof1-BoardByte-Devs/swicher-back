"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""
from fastapi import APIRouter
from app.schemas.game import GameOut, LeaveStartGame
from app.database.models import Game
from pony.orm import db_session, select
from app.database.crud import fetch_games
from app.services.game import GameService
from fastapi import HTTPException
import logging

router = APIRouter()


@router.get("/get_games", response_model=list[GameOut])
async def get_games():
    """
    Obtiene los juegos que no han comenzado.
    Returns:
        list[GameOut]: Lista de juegos que no han comenzado.
    """
    with db_session():
        games = fetch_games()
        games = [GameOut(id=g.id, name=g.name, 
                        players=[p.username for p in g.players]) for g in games if not g.started]
    return games

@router.post("/leave_game")
async def leave_game(data: LeaveStartGame):
    """
    Si el jugador es el host del juego, se elimina el juego y a los jugadores.
    Si no, se elimina al jugador de la lista de jugadores
    Args:
        player_id (int): ID del jugador.
        game_id (int): ID del juego.
    """
    try:
        GameService.leave_game(data.player_id, data.game_id)
    except Exception as e:
        logging.error(f"Error leaving game: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")