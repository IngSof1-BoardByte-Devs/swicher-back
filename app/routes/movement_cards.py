from fastapi import APIRouter, Depends
from app.schemas.movement import Movement, MovementPartial
from app.services.movement import MoveService
from app.database.session import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException

import logging

router = APIRouter()


@router.patch("/movement-cards/{card_id}", response_model=Movement, tags=["In Game"])
async def use_movement_card(card_id: int, movement_request: MovementPartial, db: Session = Depends(get_db)):
    print("estoy adentro de la funcion")  # Agrega esta línea

    move_service = MoveService(db)
    try:
        move = move_service.set_parcial_movement(movement_request.playerId, 
                                                 card_id, movement_request.index1 // 6, 
                                                 movement_request.index1 % 6, 
                                                 movement_request.index2 // 6, 
                                                 movement_request.index2 % 6)
        
        return move 
    except Exception as e:
        logging.error(f"Error updating movement card: {str(e)}")
        if str(e) == "La carta de movimiento no existe":
            raise HTTPException(status_code=404, detail=str(e))
        elif str(e) == "La carta no te pertenece":
            raise HTTPException(status_code=401, detail=str(e))
        elif str(e) == "La carta no es válida para ese movimiento":
            raise HTTPException(status_code=401, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")