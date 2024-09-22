"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""
from fastapi import APIRouter, Depends
from app.schemas.game import GameOut
from app.services.game import GameService
from typing import List
from fastapi import HTTPException
import logging

router = APIRouter()


@router.get("/get_games", response_model=List[GameOut])
async def get_games(service: GameService = Depends()):
    """
    Obtiene los juegos que no han comenzado.
    """
    try:
        return service.get_all_games()
    except Exception as e:
        logging.error(f"Error fetching games: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")