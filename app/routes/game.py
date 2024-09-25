"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""
from fastapi import APIRouter, Depends, Response
from app.schemas.game import CreateGame, GameCreateResponse, GameOut, JoinGame
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

@router.post("/create-game", response_model=None)
async def create_game(game_data: CreateGame, db: Session = Depends(get_db)):
    """
    Crea una nueva partida.
    """
    try:
        service = GameService(db)
        service.create_game(game_data)
        return {"message": "Partida creada con éxito"}, 200
    except Exception as e:
        logging.error(f"Error creating game: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/join-game")
async def join_game(game_data: JoinGame, db: Session = Depends(get_db)):
    """
    Permite a un jugador unirse a una partida.
    """
    try:
        service = GameService(db)
        service.join_game(game_data)
        return {"status": "OK"}, 201
    except Exception as e:
        logging.error(f"Error joining game: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})    