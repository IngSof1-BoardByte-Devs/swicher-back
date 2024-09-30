from sqlalchemy.orm import Session
from app.database.crud import get_game
from fastapi import WebSocket

def join_conecction(db: Session, game_id: int, ws: WebSocket):
    game = get_game(db, game_id)
    if game is None:
        ws.send_text("Create a game first")
    elif game.started:
        ws.send_text("The game has already started")
    else:
        ws.send_text("The game is in the lobby")
    return False