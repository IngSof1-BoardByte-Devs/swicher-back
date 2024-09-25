"""
Services:
Este archivo se encarga de manejar la lógica de negocio de la aplicación. Es donde implementas las 
funciones que realizan operaciones más complejas y que no están directamente relacionadas con la base de datos.
"""

from app.database.crud import create_game, create_player, fetch_games
from app.schemas.game import CreateGame, GameOut, JoinGame
from typing import Dict, List
from sqlalchemy.orm import Session

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_games(self) -> List[GameOut]:
        games = fetch_games(self.db)  # Aquí se pasa la sesión a la operación de la base de datos
        return [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games]
   
    def create_game(self, game_data: CreateGame) -> Dict:
        game = create_game(self.db, game_data.game_name)
        player = create_player(self.db, game_data.player_name)
        game.host = player
        self.db.commit()
        return {"status": "OK", "game_id": game.id}

class JoinGameService:
    def __init__(self):
        pass
    def join_game(self, game_data: JoinGame) -> Dict:
        # Lógica de negocio para unirse a una partida
        # Por ejemplo:
        if game_data.game_id <= 0:
            raise ValueError("ID de juego inválido")
        
        if not game_data.player_name:
            raise ValueError("Nombre de jugador requerido")
        
        # Simular la lógica de unirse a una partida
        # En un futuro, aquí se llamaría a la base de datos para actualizar la partida
        return {"status": "OK", "message": "Jugador unido a la partida con éxito"}