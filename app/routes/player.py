import traceback
from fastapi import APIRouter, Depends, Response
from app.schemas.player import PlayerName
from app.schemas.game import JoinGame, PlayerAndGame
from app.services.player import PlayerService
from app.services.game import GameService
from app.database.session import get_db
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging

router = APIRouter()

@router.post("/", response_model=PlayerAndGame, tags=["Home"])
async def join_game(game_data: JoinGame, db: Session = Depends(get_db)):
    """
    Permite a un jugador unirse a una partida.
    """
    service = GameService(db)
    try:
        joingame = await service.join_game(game_data)
        return PlayerAndGame(
            msg ="Jugador creado con éxito", 
            game_id= joingame.game_id,
            player_id= joingame.player_id 
            
        )
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


@router.delete("/{id}", tags=["In Game"])
async def leave_game(id: int, db: Session = Depends(get_db)):
    service = GameService(db)
    try:
        id_player = id
        await service.leave_game(id_player)
        return { "msg": "Salió del juego" }
    except Exception as e:
        logging.error(f"Error leaving game: {str(e)}")
        if str(e) == "Jugador no encontrado":
            raise HTTPException(status_code=404, detail=str(e))
        if str(e) == "No puede abandonar el jugador de turno":
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{id}/turn", tags=["In Game"])
async def end_turn(id: int, db: Session = Depends(get_db)):
    """
    Termina el turno del jugador.
    """
    service = GameService(db)
    try:
        id_player = id
        await service.change_turn(id_player)
        return {"msg": "Turno finalizado"}
    
    except Exception as e:
        logging.error(f"Error end turn: {str(e)}")
        logging.error("Traceback: %s", traceback.format_exc())
        if str(e) in ["Partida no iniciada", "Jugador no encontrado"]: 
            raise HTTPException(status_code=404, detail=str(e))
        elif str(e) == "No es turno del jugador":
            raise HTTPException(status_code=401, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")
