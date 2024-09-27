"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""

from fastapi import APIRouter, Depends
from app.schemas.game import GameOut, LeaveStartGame
from app.services.game import GameService
from app.database.session import get_db  # Importa la función para obtener la sesión
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging

router = APIRouter()

@router.get("/get_games", response_model=List[GameOut])
async def get_games(db: Session = Depends(get_db)):
    """
    Obtiene los juegos que no han comenzado.
    """

    service = GameService(db)  # Crea la instancia del servicio con la sesión inyectada
    try:
        return service.get_all_games()
    except Exception as e:
        logging.error(f"Error fetching games: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/leave_game")
async def leave_game(data: LeaveStartGame, db: Session = Depends(get_db)):
    """
    Si el jugador es el host del juego, se elimina el juego y a los jugadores.
    Si no, se elimina al jugador de la lista de jugadores
    Args:
        player_id (int): ID del jugador.
        game_id (int): ID del juego.
    """
    service = GameService(db)
    try:
        service.leave_game(data.player_id, data.game_id)
        return {"status": "OK"}, 200
    except Exception as e:
        logging.error(f"Error leaving game: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid player or game")
