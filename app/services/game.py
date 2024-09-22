"""
Services:
Este archivo se encarga de manejar la lógica de negocio de la aplicación. Es donde implementas las 
funciones que realizan operaciones más complejas y que no están directamente relacionadas con la base de datos.
"""

from app.database.crud import fetch_games, leave_game
from app.database.models import Game, Player
from app.schemas.game import GameOut
from typing import List

class GameService:
    def get_all_games(self) -> List[GameOut]:
        games = fetch_games()
        return [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games]
    
    def leave_game(self, player_id: int, game_id: int):
        player = Player[player_id]
        game = Game[game_id]
        if player in game.players:
            leave_game(player, game)