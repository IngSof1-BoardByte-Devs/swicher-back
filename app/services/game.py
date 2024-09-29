"""
Services:
Este archivo se encarga de manejar la lógica de negocio de la aplicación. Es donde implementas las 
funciones que realizan operaciones más complejas y que no están directamente relacionadas con la base de datos.
"""

from app.database.models import Game, Player
from app.database.crud import *
from app.schemas.game import *
from app.schemas.player import *
from app.services.movement import MoveService
from app.services.figures import FigureService
from app.services.board import BoardService
from app.websocket_manager import ConnectionManager
from typing import Dict, List
from sqlalchemy.orm import Session
import random

class GameService:
    def __init__(self, db: Session):
        self.db = db
        self.ws = ConnectionManager()

    def get_all_games(self) -> List[GameOut]:
        games = fetch_games(self.db)
        game_list = [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games if not g.started]
        return game_list

    def get_game(self, game_id: int) -> List[SingleGameOut]:
        game = get_game(self.db, game_id)
        if game == None:
            raise Exception("Error: Game not found")
        if game.started:
            status = "Started"
        else:
            status = "Not started"
        players = [PlayerOut(username=player.username, id=player.id) for player in game.players]
        return SingleGameOut(id=game.id, name=game.name,status=status , players= players)

    def leave_game(self, player_id: int, game_id: int):
        player = get_player(self.db, player_id)
        if not player:
            raise Exception("No existe el jugador")
        
        game = get_game(self.db, game_id)
        if not game:
            raise Exception("No existe la partida")
        
        if player not in game.players:
            raise Exception("El jugador no esta en esa partida")
        if len(game.players) == 1:
            raise Exception("No puede abandonar partida el jugador cuando es uno solo")
        
        delete_player(self.db,player, game)
        # Avisar el ganador por websocket
        # delete_all_game(self.db, game)
   
    def create_game(self, game_data: CreateGame) -> GameLeaveCreateResponse:
        game = create_game(self.db, game_data.game_name)
        player = create_player(self.db, game_data.player_name, game)
        game.host = player
        self.db.commit()
        json_ws = {"game_id": game.id, "game_name": game.name, "num_players": len(game.players)}
        json_ws = json.dumps(json_ws)
        self.ws.broadcast(json_ws, 0)
        return GameLeaveCreateResponse(player_id=player.id, game_id=game.id)
    
    def join_game(self, data: JoinGame) -> GameLeaveCreateResponse:
        game = get_game(self.db, data.game_id)
        
        if game == None:
            raise Exception("Error: User tries to join a non-existent game")
        elif game.started:
            raise Exception("Error: The game has already begun")
        if len(game.players) >= 4:
            raise Exception("Error: Maximum players allowed")
        player = create_player(self.db, data.player_name, game)

        return GameLeaveCreateResponse(player_id=player.id, game_id=game.id)
    

    def start_game(self, game_data: StartGame) -> Dict:
        game = get_game_by_id(self.db, game_data.game_id)
        # Manejo de errores
        if not game:
            raise ValueError("Juego no encontrado")
        elif game.host.id != game_data.player_id:
            raise ValueError("Solo el anfitrión puede iniciar el juego")
        elif len(game.players) < 2:
            raise ValueError("Se necesitan al menos dos jugadores para iniciar el juego")
        elif game.started:
            raise ValueError("El juego ya ha comenzado")
        
        # Actualizar el estado del juego
        put_start_game(self.db, game)

        # Asignar los turnos a los jugadores
        players = List[Player]
        players = game.players
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

    def change_turn(self, player_id: int):
        # Obtener el juego asociado al jugador
        game = get_game_by_player_id(self.db, player_id)
        if not game:
            raise Exception("Error: No existe jugador o no existe la partida")
        
        # Verificar si el juego ha comenzado
        if not game.started:
            raise Exception("Error: La partida todavía no se inicializó")
        
        # Obtener el jugador
        player = get_player(self.db, player_id)
        
        # Verificar si es el turno del jugador
        if player.turn == game.turn:
            # Actualizar el turno del juego
            update_turn_game(self.db, game)
            
            # Verificar si el turno es válido
            if game.turn > len(game.players) or game.turn <= 0:
                raise Exception("Error: Turno de jugador que no existe")
        else:
            raise Exception("Error: El turno del jugador no corresponde con el turno de la partida")