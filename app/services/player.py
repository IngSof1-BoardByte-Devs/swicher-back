from app.database.crud import get_players_in_game
from app.schemas.player import PlayerRequest
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from typing import List

class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def get_players(self, player_id: int):
        list_players = []
        players = get_players_in_game(self.db, player_id)
        for player in players:
            list_players.append(PlayerRequest(player_id=player.id, player_name=player.username))
        json_compatible_payload = jsonable_encoder(list_players)

        return json_compatible_payload
