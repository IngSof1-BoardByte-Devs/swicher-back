from fastapi import APIRouter, status
from app.database.models import Player
from pony.orm import db_session, select
from fastapi.responses import JSONResponse


router = APIRouter()

@router.post("/crear_player")
async def crear_player(username : str):
    with db_session():
        player = Player(username=username)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Player created successfully"})

@router.delete("/borrar_player")
async def borrar_player(username : str):
    with db_session():
        player = select(p for p in Player if p.username == username).first()
        if player:
            player.delete()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Player delete successfully"})