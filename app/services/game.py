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
        games = fetch_games(self.db)
        game_list = [GameOut(id=g.id, name=g.name, num_players=len(g.players)) for g in games if not g.started]
        return game_list

    def get_game(self, game_id: int) -> List[SingleGameOut]:
        game = get_game(self.db, game_id)
        if game == None:
            raise Exception("Error: Game not found")
        players = [PlayerOut(username=player.username, id=player.id, turn=player.turn) for player in game.players]
        return SingleGameOut(id=game.id, name=game.name,started=game.started, turn=game.turn, bloqued_color=game.bloqued_color, players= players)

    async def leave_game(self, player_id: int):
        player = get_player(self.db, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        
        game = get_game_by_player_id(self.db, player_id)
        
        if player not in game.players:
            raise HTTPException(status_code=404, detail="Player not in game")
        
        delete_player(self.db,player, game)
        self.db.commit()

        json_ws1 = {"event": "player_left", "data": {"player_id": player.id}}
        await manager.broadcast(json.dumps(json_ws1), game.id)
        
        if len(game.players) == 1:
            delete_all_game(self.db, game)

        return {"status": "OK", "message": "Player left the game"}
   
    async def create_game(self, game_data: CreateGame) -> GameLeaveCreateResponse:
        game = create_game(self.db, game_data.game_name)
        player = create_player(self.db, game_data.player_name, game)
        game.host = player
        self.db.commit()
        json_ws = {"event": "new_game", "data": {"id": game.id, "name": game.name, "num_players": len(game.players)}}
        await manager.broadcast(json.dumps(json_ws), 0)
        return GameLeaveCreateResponse(player_id=player.id, game_id=game.id)
    
    async def join_game(self, data: JoinGame) -> GameLeaveCreateResponse:
        game = get_game(self.db, data.game_id)
        
        if game == None:
            raise Exception("Error: User tries to join a non-existent game")
        elif game.started:
            raise Exception("Error: The game has already begun")
        if len(game.players) >= 4:
            raise Exception("Error: Maximum players allowed")
        player = create_player(self.db, data.player_name, game)

        json_ws1 = {"event": "join_game", "data": {"player_id": player.id, "player_name": player.username}}
        json_ws2 = {"event": "new_player", "data": {"game_id": game.id}}
        await manager.broadcast(json.dumps(json_ws1), game.id)
        await manager.broadcast(json.dumps(json_ws2), 0)

        return GameLeaveCreateResponse(player_id=player.id, game_id=game.id)
    

    async def start_game(self, player_id: int) -> Dict:
        player = get_player(self.db, player_id)
        if not player:
            raise HTTPException(status_code=404, detail="Player not found")
        game = get_game_by_player_id(self.db, player_id)

        # Manejo de errores
        if game.started:
            raise HTTPException(status_code=400, detail="The game has already started")
        elif int(game.host.id) != int(player_id):
            print(game.host.id, player_id, game.host.id == player_id)
            raise HTTPException(status_code=403, detail="Only the game owner can start the game")
        elif len(game.players) < 2:
            raise HTTPException(status_code=400, detail="The game must have at least 2 players")
        
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

        #--------------------------hace falta el id?
        ws_json = {"event": "start_game", "data": {"game_id": game.id}}
        await manager.broadcast(json.dumps(ws_json), game.id)
        await manager.broadcast(json.dumps(ws_json), 0)

        return {"status": "OK", "message": "Game started"}

    async def change_turn(self, player_id: int):
        # Obtener el juego asociado al jugador
        game = get_game_by_player_id(self.db, player_id)
        if not game:
            raise Exception("Error: Game not found")
        
        # Verificar si el juego ha comenzado
        if not game.started:
            raise Exception("Error: The game has not started")
        
        # Obtener el jugador
        player = get_player(self.db, player_id)
        
        # Verificar si es el turno del jugador
        if player.turn == game.turn:
            # Actualizar el turno del juego
            update_turn_game(self.db, game)
            
            # Verificar si el turno es válido
            if game.turn > len(game.players) or game.turn <= 0:
                raise Exception("Error: Invalid turn")
        else:
            raise Exception("Error: The player is not in turn")
        
        json_ws = {"event": "change_turn", "data": {"turn": game.turn}}
        await manager.broadcast(json.dumps(json_ws), game.id)