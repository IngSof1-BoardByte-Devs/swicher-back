"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""

from app.schemas.board import BoardOut
from app.schemas.movement import MovementOut, MovementRequest
from app.services.board import BoardService
from fastapi import APIRouter, Depends, Response
from app.schemas.game import *
from app.schemas.player import PlayerRequest
from app.schemas.figure import FigureOut
from app.services.game import GameService
from app.services.figures import FigureService
from app.services.movement import MoveService
from app.database.session import get_db  # Importa la función para obtener la sesión
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging



router = APIRouter()

@router.get("/get_game/{game_id}", response_model=SingleGameOut, tags=["Lobby"])
async def get_game(game_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los jugadores en el juego.
    """
    service = GameService(db)
    try:
        return service.get_game(game_id)
    except Exception as e:
        logging.error(f"Error fetching players: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/", response_model=List[GameOut], tags=["Home"])
async def get_games(db: Session = Depends(get_db)):
    """
    Obtiene los juegos que no han comenzado.
    """

    service = GameService(db)
    try:
        return service.get_all_games()
    except Exception as e:
        logging.error(f"Error fetching games: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/leave_game", tags=["In Game"])
async def leave_game(data: LeaveStartGame, db: Session = Depends(get_db), tags=["In Game"]):
    """
    Ningun jugador puede abandonar una partida no empezada
    Args:
        player_id (int): ID del jugador.
        game_id (int): ID del juego.
    """
    service = GameService(db)
    try:
        return service.leave_game(data.player_id, data.game_id)
    except Exception as e:
        logging.error(f"Error leaving game: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)}) 
        
@router.post("/", response_model=GameLeaveCreateResponse, tags=["Home"])
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
    
@router.post("/{player_id}", tags=["Lobby"])
async def start_game(player_id = int, db: Session = Depends(get_db)):
    """
    Inicia una partida.Home
    """
    service = GameService(db)
    try:
        return service.start_game(player_id)
    except Exception as e:
        logging.error(f"Error starting game: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})

@router.get("/figure-cards/{player_id}", response_model=List[FigureOut], tags=["In Game"])
async def get_figure_cards(player_id: int, db: Session = Depends(get_db)):
    """
    Obtiene las cartas de una figura.
    """
    service = FigureService(db)
    try:
        return service.get_figures(player_id)
    except Exception as e:
        logging.error(f"Error getting figure cards: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})

@router.get("/board/{player_id}", response_model=BoardOut, tags=["In Game"])
async def board(player_id : int, db: Session = Depends(get_db)):
    """
    Obtiene el tablero
    """

    service = BoardService(db)
    try:
        colors = service.get_board_values(player_id)
        result = BoardOut
        result.board = colors
        return result
    except Exception as e:
        logging.error(f"Error get board: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})

@router.post("/end-turn", tags=["In Game"])
async def end_turn(player: PlayerRequest, db: Session = Depends(get_db)):
    """
    Termina el turno del jugador.
    """
    service = GameService(db)
    try:
        service.change_turn(player.player_id)
        return {"status": "OK"}
    
    except Exception as e:
        logging.error(f"Error end tunr: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)})

@router.get("/{player_id}/move-cards", response_model=List[MovementOut], tags=["In Game"])
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
