from fastapi import APIRouter, Depends
from app.schemas.figure import *
from app.services.figures import FigureService
from app.database.session import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException

import logging

router = APIRouter()

@router.patch("/{card_id}/", tags=["In Game"], response_model=FigUpdate)
async def recognize_figure(card_id: int, figure: FigureDiscard, db: Session = Depends(get_db)):
    try:
        figureService = FigureService(db)
        response = await figureService.update_figure_status(card_id, figure.playerId, figure.color)
        return response
    except Exception as e:
        logging.error(f"Error recognize_figure: {e}")
        if str(e) == "La carta de figura no existe":
            raise HTTPException(status_code=404, detail=str(e))
        elif str(e) == "La carta/jugador no pertenece a este juego":
            raise HTTPException(status_code=401, detail=str(e))
        elif str(e) in ["La carta debe estar en la mano",
                        "La figura es del color prohibido",
                        "Color inválido",
                        "El jugador no puede descartar una carta bloqueada",
                        "El jugador ya tiene una carta bloqueada",
                        "El jugador debe tener mas de dos cartas para ser bloqueado"]:
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "No es tu turno":
            raise HTTPException(status_code=403, detail=str(e))
        elif str(e) == "Función de bloquear figura no implementada":
            raise HTTPException(status_code=501, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")