import json
from sqlalchemy.orm import Session
from app.database.crud import get_game
from fastapi import WebSocket

def join_conecction(db: Session, game_id: int, ws: WebSocket):
    game = get_game(db, game_id)
    if game is None:
        json_ws = {"event": "join_ws", "data": {"message": "Game not found", "status": 0}}
        ws.send_text(json.dumps(json_ws))
        return False
    elif game.started:
        json_ws = {"event": "join_ws", "data": {"message": "Game already started", "status": 1}}
        ws.send_text(json.dumps(json_ws))
    else:
        json_ws = {"event": "join_ws", "data": {"message": "You have joined the game", "status": 2}}
        ws.send_text(json.dumps(json_ws))
    return True