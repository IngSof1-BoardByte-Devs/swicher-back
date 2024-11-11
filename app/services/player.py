from app.database.crud import get_players_in_game
from app.schemas.player import PlayerName, Message
from app.core.websocket import manager
from sqlalchemy.orm import Session
from app.database.crud import get_player
from typing import List
import json

class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def get_players(self, player_id: int) -> List[PlayerName]:
        list_players = []
        players = get_players_in_game(self.db, player_id)
        for player in players:
            list_players.append(PlayerName(username=player.username))
        return list_players
    
    async def send_message(self, player_id: int, message: Message):
        player = get_player(self.db, player_id)
        if not player:
            raise Exception("Jugador no encontrado")
        game = player.game
        
        ws_json = {
            "event": "message.chat",
            "payload": {
                "username": player.username,
                "message": message.message
            }
        }
        await manager.broadcast(json.dumps(ws_json), game.id)
        return {"status": "OK", "message": "Message sent"}
