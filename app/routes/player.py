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
        return service.join_game(game_data)
    except Exception as e:
        logging.error(f"Error joining game: {str(e)}")
        raise HTTPException(status_code=400, detail={"status": "ERROR", "message": str(e)}) 