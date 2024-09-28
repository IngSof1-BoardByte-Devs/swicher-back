from app.database.crud import get_players_in_game
from app.schemas.player import PlayerName
from sqlalchemy.orm import Session
from typing import List

class PlayerService:
    def __init__(self, db: Session):
        self.db = db

    def get_players(self, player_id: int) -> List[PlayerName]:
        list_players = []
        players = get_players_in_game(self.db, player_id)
        for player in players:
            list_players.append(PlayerName(username=player.username))
        return list_players
