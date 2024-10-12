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
from app.core.websocket import manager
from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
import random

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_games(self) -> List[GameOut]:
        """ Obtiene todas las partidas """
        games = fetch_games(self.db)
        game_list = [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games if not g.started]
        return game_list


    def get_game(self, game_id: int) -> List[SingleGameOut]:
        """ Obtiene una partida por su id """
        game = get_game(self.db, game_id)
        if game == None:
            raise Exception("Partida no encontrada")
        players = [PlayerOut(username=player.username, id=player.id, turn=player.turn) for player in game.players]
        return SingleGameOut(id=game.id, name=game.name,started=game.started, turn=game.turn, bloqued_color=game.bloqued_color, players= players)


    async def leave_game(self, player_id: int):
        """ Elimina un jugador de una partida """
        player = get_player(self.db, player_id)
        if not player:
            raise Exception("Jugador no encontrado")
        
        game = get_game_by_player_id(self.db, player_id)

        if player not in game.players:
            raise Exception("Player not in game")
        
        delete_player(self.db,player, game)
        self.db.commit()

        json_ws = {"event": "player.left", "payload": {"game_id": game.id, "username": player.username}}
        await manager.broadcast(json.dumps(json_ws), game.id)
        await manager.broadcast(json.dumps(json_ws), 0)
        
        if len(game.players) == 1:
            delete_all_game(self.db, game)

        return {"status": "OK", "message": "Player left the game"}
   

    async def create_game(self, game_data: CreateGame) -> GameLeaveCreateResponse:
        """ Crea una partida """
        if not game_data.player_name:
            raise Exception("El jugador debe tener un nombre")
        elif not game_data.game_name:
            raise Exception("La partida debe tener un nombre")
        game = create_game(self.db, game_data.game_name)
        player = create_player(self.db, game_data.player_name, game)
        game.host = player
        self.db.commit()
        json_ws = {"event": "game.new", "payload": {"game_id": game.id, "name": game.name, "players": len(game.players)}}
        await manager.broadcast(json.dumps(json_ws), 0)
        return GameLeaveCreateResponse(player_id=player.id, game_id=game.id)
   

    async def join_game(self, data: JoinGame) -> GameLeaveCreateResponse:
        """ Un jugador se une a una partida """
        if not data.player_name:
            raise Exception("El jugador debe tener un nombre")
        
        game = get_game(self.db, data.game_id)

        if game == None:
            raise Exception("Partida no encontrada")
        elif game.started:
            raise Exception("Partida ya iniciada")
        if len(game.players) >= 4:
            raise Exception("Partida con máximo de jugadores permitidos")
        player = create_player(self.db, data.player_name, game)

        json_ws = {"event": "player.new", "payload": {"game_id": game.id, "username": player.username}}
        await manager.broadcast(json.dumps(json_ws), game.id)
        await manager.broadcast(json.dumps(json_ws), 0)

        return GameLeaveCreateResponse(player_id=player.id, game_id=game.id)
    

    async def start_game(self, player_id: int) -> Dict:
        """ Inicia una partida """
        player = get_player(self.db, player_id)
        if not player:
            raise Exception("Jugador no encontrado")
        game = get_game_by_player_id(self.db, player_id)

        # Manejo de errores
        if game.started:
            raise Exception("La partida ya se inició")
        elif int(game.host.id) != int(player_id):
            raise Exception("Sólo el dueño puede iniciar la partida")
        elif len(game.players) < 2 or len(game.players) > 4:
            raise Exception("La partida debe tener entre 2 a 4 jugadores para iniciar")
        
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

        ws_json = {"event": "game.start", "payload": {"game_id": game.id}}
        await manager.broadcast(json.dumps(ws_json), game.id)
        await manager.broadcast(json.dumps(ws_json), 0)

        return {"status": "OK", "message": "Game started"}


    async def change_turn(self, player_id: int):
        """ Cambia el turno de un jugador """
        # Obtener el jugador
        player = get_player(self.db, player_id)
        if not player:
            raise Exception("Jugador no encontrado")
        
        # Obtener el juego asociado al jugador
        game = get_game_by_player_id(self.db, player_id)
        
        # Verificar si el juego ha comenzado
        if not game.started:
            raise Exception("Partida no iniciada")
        if player.turn == game.turn:
            # Actualizar el turno del juego
            update_turn_game(self.db, game)
            
            # Verificar si el turno es válido
            if game.turn > len(game.players) or game.turn <= 0:
                raise Exception("Error: Invalid turn")
        else:
            raise Exception("No es turno del jugador")
        
        json_ws = {"event": "game.turn", "payload": {"turn": game.turn}}
        await manager.broadcast(json.dumps(json_ws), game.id)
