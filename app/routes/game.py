"""
Los archivos de rutas son los encargados de manejar las peticiones HTTP que llegan al servidor.
Es donde se definen los endpoints y se especifica qué funciones se ejecutarán al recibir una 
petición en un endpoint específico.
"""

from app.schemas.board import BoardOut
from app.schemas.movement import Movement, MovementOut, MovementPartial, MovementRequest
from app.services.board import BoardService
from fastapi import APIRouter, Depends, Response
from app.schemas.game import *
from app.schemas.player import PlayerRequest
from app.schemas.figure import FigureOut
from app.services.game import GameService
from app.services.figures import FigureService
from app.services.movement import MoveService
from app.database.session import get_db
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging



router = APIRouter()

""" @router.get("/{game_id}", response_model=SingleGameOut, tags=["Lobby"])
async def get_game(game_id: int, db: Session = Depends(get_db)):

    service = GameService(db)
    try:
        return service.get_game(game_id)
    except Exception as e:
        logging.error(f"Error fetching players: {str(e)}")
        if str(e) == "Partida no encontrada": 
            logging.error("Tiro HTTPException")
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error") """
    

@router.post("/", response_model=PlayerAndGame, tags=["Home"])
async def create_game(game_data: CreateGame, db: Session = Depends(get_db)):
    """
    Crea una nueva partida.
    """
    service = GameService(db)
    try:
        return await service.create_game(game_data)
    except Exception as e:
        logging.error(f"Error creating game: {str(e)}")
        if str(e) == "La partida debe tener un nombre" or str(e) == "El jugador debe tener un nombre": 
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{id}/started", tags=["Lobby"])
async def start_game(player_id = int, db: Session = Depends(get_db)):
    """
    Inicia una partida.
    """
    service = GameService(db)
    try:
        return await service.start_game(player_id)
    except Exception as e:
        logging.error(f"Error starting game: {str(e)}")
        if str(e) == "La partida ya se inició" or str(e) == "La partida debe tener entre 2 a 4 jugadores para iniciar":
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "Sólo el dueño puede iniciar la partida":
            raise HTTPException(status_code=401, detail=str(e))
        elif str(e) == "Jugador no encontrado":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
       

@router.get("/{id_game}/figure-cards", response_model=List[FigureOut], tags=["In Game"])
async def get_figure_cards(id_game: int, db: Session = Depends(get_db)):
    """
    Obtiene todas las cartas de figura que tienen los jugadores en la mano.
    """
    service = FigureService(db)
    try:
        return service.get_figures(id_game)
    except Exception as e:
        logging.error(f"Error getting figure cards: {str(e)}")
        if str(e) == "Partida no iniciada":
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "Partida no encontrada":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{id_game}/board", response_model=BoardOut, tags=["In Game"])
async def board(id_game : int, db: Session = Depends(get_db)):
    """
    Obtiene el tablero
    """
    service = BoardService(db)
    try:
        response = await service.get_board_values(id_game)
        return response
    except Exception as e:
        logging.error(f"Error get board: {str(e)}")
        if str(e) == "Partida no iniciada":
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "Partida no encontrada":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


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
        if str(e) == "Partida no iniciada":
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "Jugador no encontrado":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/{game_id}/revert-moves", tags=["In Game"])
async def revert_moves(game_id: int, revert_request: RevertRequest, db: Session = Depends(get_db)):
    service = MoveService(db)

    try:
        await service.revert_moves(PlayerAndGame(player_id=revert_request.player_id,game_id=game_id))
        return { "message" : "Turn reverted successfully" }
    
    except Exception as e:
        if "No hay cambios para revertir" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        elif "No tienes autorización para revertir estos cambios" in str(e):
            raise HTTPException(status_code=401, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")