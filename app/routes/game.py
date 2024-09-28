"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""

from app.schemas.board import BoardOut
from app.schemas.movement import MovementOut, MovementRequest
from app.services.board import BoardService
from fastapi import APIRouter, Depends, Response
from app.schemas.game import CreateGame, GameLeaveCreateResponse, GameOut, JoinGame, StartGame, LeaveStartGame
from app.services.game import GameService
from app.database.session import get_db  # Importa la función para obtener la sesión
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging

from app.services.movement import MoveService

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)


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
        return service.leave_game(data.player_id, data.game_id)
    except Exception as e:
        logging.error(f"Error leaving game: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid player or game")
        
@router.post("/create-game", response_model=GameLeaveCreateResponse)
async def create_game(game_data: CreateGame, db: Session = Depends(get_db)):
    """
    Crea una nueva partida.
    """
    try:
        service = GameService(db)
        return service.create_game(game_data)
    except Exception as e:
        logging.error(f"Error creating game: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/join-game", response_model=GameLeaveCreateResponse)
async def join_game(game_data: JoinGame, db: Session = Depends(get_db)):
    """
    Permite a un jugador unirse a una partida.
    """
    try:
        service = GameService(db)
        return service.join_game(game_data)
    except Exception as e:
        logging.error(f"Error joining game: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})    
    
@router.post("/start-game")
async def start_game(game_data: StartGame, db: Session = Depends(get_db)):
    """
    Inicia una partida.
    """
    try:
        service = GameService(db)
        service.start_game(game_data)
        return {"status": "OK"}, 200
    except Exception as e:
        logging.error(f"Error starting game: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})

"""GET /board
Devuelve el estado del tablero de la partida.
Request Body: {"player_id": "int"}
Response:
200 OK: { "board": [color: “int”, …]}
400 ERROR: {"status": "ERROR", "message": "string"}"""

@router.get("/board", response_model=BoardOut)
async def board(player_id : int, db: Session = Depends(get_db)):
    """
    Obtiene el tablero
    """

    service = BoardService(db)  # Crea la instancia del servicio con la sesión inyectada
    try:
        colors = service.get_board_values(player_id)
        result = BoardOut
        result.board = colors
        return result
    except Exception as e:
        logging.error(f"Error fetching games: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/movement-cards", response_model=List[MovementOut])
async def get_movement_cards(player_id: int, db: Session = Depends(get_db)):
    """
    Obtiene las cartas de movimiento de un jugador.
    """
    service = MoveService(db)
    try:
        movements = service.get_movements(player_id)
        return movements
    except Exception as e:
        logging.error(f"Error fetching movements: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})