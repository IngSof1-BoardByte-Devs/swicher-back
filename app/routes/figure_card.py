from fastapi import APIRouter, Depends
from app.schemas.figure import *
from app.services.figures import FigureService
from app.database.session import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException

import logging

router = APIRouter()

@router.put("/{id}/status", tags=["In Game"])
async def recognize_figure(card_id: int, playerId: FigureDiscard, db: Session = Depends(get_db)):
    try:
        figureService = FigureService(db)
        await figureService.update_figure_status(card_id, playerId.playerId)
        return {"msg":"Carta usanda con exito"}
    except Exception as e:
        logging.error(f"Error recognize_figure: {e}")
        if str(e) == "La carta de figura no existe":
            raise HTTPException(status_code=404, detail=str(e))
        elif str(e) == "La carta/jugador no pertenece a este juego":
            raise HTTPException(status_code=401, detail=str(e))
        elif str(e) == "La carta debe estar en la mano":
            raise HTTPException(status_code=400, detail=str(e))
        elif str(e) == "No es tu turno":
            raise HTTPException(status_code=403, detail=str(e))
        elif str(e) == "Función de bloquear figura no implementada":
            raise HTTPException(status_code=501, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")