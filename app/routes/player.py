from fastapi import APIRouter, Depends, Response
from app.schemas.player import PlayerName
from app.services.player import PlayerService
from app.database.session import get_db
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException
import logging

router = APIRouter()

@router.get("/get_player{player_id}", response_model=List[PlayerName])
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """
    Obtiene los jugadores en el juego.
    """
    service = PlayerService(db)
    try:
        return service.get_players(player_id)
    except Exception as e:
        logging.error(f"Error fetching players: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

