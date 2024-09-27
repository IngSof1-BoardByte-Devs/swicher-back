from app.database.models import Game, Player
from app.database.crud import *
from app.schemas.game import *
from app.services.movement import MoveService
from app.services.figures import FigureService
from app.services.board import BoardService
from typing import Dict, List
from sqlalchemy.orm import Session
import random

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_games(self) -> List[GameOut]:
        games = fetch_games(self.db)  # Aquí se pasa la sesión a la operación de la base de datos
        game_list = [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games]
        # Inprimir todos os jugadores de todas las partidas
        return game_list


    def leave_game(self, player_id: int, game_id: int):
        player = get_player_by_id(self.db, player_id)
        game = get_game_by_id(self.db, game_id)
        if not player or not game or player not in game.players:
            print("acá debería entrar")
            raise Exception("Invalid player or game")
        else:
            print("acá no debería entrar")
            delete_player(player, game)
   
    def create_game(self, game_data: CreateGame) -> Dict:
        game = create_game(self.db, game_data.game_name)
        player = create_player(self.db, game_data.player_name, game)
        game.host = player
        self.db.commit()
        return {"status": "OK", "game_id": game.id}
    
    def join_game(self, game_data: JoinGame) -> Dict:
        # Lógica de negocio para unirse a una partida
        # Por ejemplo:
        if game_data.game_id <= 0:
            raise ValueError("ID de juego inválido")
        
        if not game_data.player_name:
            raise ValueError("Nombre de jugador requerido")
        
        game = get_game(self.db, game_data.game_id)
        
        create_player(self.db, game_data.player_name, game)
        return {"status": "OK", "message": "Jugador unido a la partida con éxito"}
    

    def start_game(self, game_data: StartGame) -> Dict:

        game = get_game_by_id(self.db, game_data.game_id)

        # Manejo de errores
        if not game:
            raise ValueError("Juego no encontrado")
        elif game.host.id != game_data.player_id:
            raise ValueError("Solo el anfitrión puede iniciar el juego")
        
        # Actualizar el estado del juego
        put_start_game(self.db, game)

        # Asignar los turnos a los jugadores
        players = List[Player]
        random.shuffle(players)
        for i in range(len(players)):
            player = players[i]
            put_asign_turn(self.db, player, i+1)

        # Crear el mazo de movimientos
        move_service = MoveService(self.db)
        move_service.create_movement_deck(game.id)

        # Crear el mazo de figuras
        figure_service = FigureService(self.db)
        figure_service.create_figure_deck(game.id)

        # Crear el tablero
        board_service = BoardService(self.db)
        board_service.create_board(game.id)
