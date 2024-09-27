"""
Services:
Este archivo se encarga de manejar la lógica de negocio de la aplicación. Es donde implementas las 
funciones que realizan operaciones más complejas y que no están directamente relacionadas con la base de datos.
"""
from app.database.crud import *
from app.schemas.game import GameOut, JoinGame
from typing import List
from sqlalchemy.orm import Session

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_games(self) -> List[GameOut]:
        games = fetch_games(self.db)  # Aquí se pasa la sesión a la operación de la base de datos
        return [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games]
    
    def join_game(self, data: JoinGame):
        game = get_game(self.db, data.game_id)
        
        if game == None:
            raise Exception("Error: User tries to join a non-existent game")
        elif game.started:
            raise Exception("Error: The game has already begun")
        if len(game.players.all()) <= 4:
            raise Exception("Error: Maximum players allowed")
        create_player(self.db, data.player_name, game)
