from fastapi import APIRouter, Depends
from app.schemas.figure import *
from app.services.figures import FigureService
from app.database.session import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException

import logging

router = APIRouter()

@router.patch("/{card_id}", tags=["In Game"], response_model=FigUpdate)
async def recognize_figure(card_id: int, player_id: int, db: Session = Depends(get_db)):
    try:
        figureService = FigureService(db)
        response = await figureService.update_figure_service_status(card_id, player_id)
        return response
    except Exception as e:
        logging.error(f"Error moving card: {e}")
        raise HTTPException(status_code=500, detail="Error moving card")