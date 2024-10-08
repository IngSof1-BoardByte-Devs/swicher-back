from fastapi import APIRouter, Depends, Response
from app.schemas.player import PlayerName
from app.schemas.game import JoinGame, GameLeaveCreateResponse
from app.services.player import PlayerService
from app.services.game import GameService
from app.database.session import get_db
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging

router = APIRouter()

@router.post("/", response_model=GameLeaveCreateResponse, tags=["Home"])
async def join_game(game_data: JoinGame, db: Session = Depends(get_db)):
    """
    Permite a un jugador unirse a una partida.
    """
    try:
        service = GameService(db)
        return await service.join_game(game_data)
    except Exception as e:
        logging.error(f"Error joining game: {str(e)}")
        if (str(e) == "El jugador debe tener un nombre"
            or str(e) == "Partida ya iniciada"
            or str(e) == "Partida con máximo de jugadores permitidos"):
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "Partida no encontrada":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{id_player}", tags=["In Game"])
async def leave_game(id_player: int, db: Session = Depends(get_db)):
    """
    Ningun jugador puede abandonar una partida no empezada
    Args:
        id_player (int): ID del jugador.
    """
    service = GameService(db)
    try:
        return await service.leave_game(id_player)
    except Exception as e:
        logging.error(f"Error leaving game: {str(e)}")
        if str(e) == "Jugador no encontrado":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{id_player}/turn", tags=["In Game"])
async def end_turn(id_player: int, db: Session = Depends(get_db)):
    """
    Termina el turno del jugador.
    """
    service = GameService(db)
    try:
        await service.change_turn(id_player)
        return {"status": "OK", "message": "Turn ended"}
    
    except Exception as e:
        logging.error(f"Error end turn: {str(e)}")
        if str(e) == "Partida no iniciada":
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "No es turno del jugador":
            raise HTTPException(status_code=401, detail=str(e))
        elif str(e) == "Jugador no encontrado":
            raise HTTPException(status_code=404, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
