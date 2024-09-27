"""
Services:
Este archivo se encarga de manejar la lógica de negocio de la aplicación. Es donde implementas las 
funciones que realizan operaciones más complejas y que no están directamente relacionadas con la base de datos.
"""

from app.database.crud import *
from app.database.models import Game, Player
from app.schemas.game import GameOut
from typing import List
from sqlalchemy.orm import Session

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_games(self) -> List[GameOut]:
        games = fetch_games(self.db)  # Aquí se pasa la sesión a la operación de la base de datos
        return [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games]
    
    # Si no se encuentra el jugador o el juego, se lanza una excepción 400
    def leave_game(self, player_id: int, game_id: int):
        player = get_player_by_id(self.db, player_id)
        game = get_game_by_id(self.db, game_id)
        if not player or not game or player not in game.players:
            print("acá debería entrar")
            raise Exception("Invalid player or game")
        else:
            print("acá no debería entrar")
            delete_player(player, game)
