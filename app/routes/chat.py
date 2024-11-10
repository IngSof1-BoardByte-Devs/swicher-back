from fastapi import APIRouter, Depends, Response
from app.database.session import get_db
from sqlalchemy.orm import Session
from app.schemas.player import Message
from app.services.player import PlayerService
from fastapi import HTTPException

router = APIRouter()

@router.post("/{player_id}", response_model=Message, tags=["Chat"])
async def send_message(player_id: int, message: Message, db: Session = Depends(get_db)):
    try:    
        service = PlayerService(db)
        return await service.send_message(player_id, message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")