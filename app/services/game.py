"""
Services:
Este archivo se encarga de manejar la lógica de negocio de la aplicación. Es donde implementas las 
funciones que realizan operaciones más complejas y que no están directamente relacionadas con la base de datos.
"""

from app.database.models import Game, Player
from app.database.crud import *
from app.schemas.figure import FigureOut
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
import json


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
        """ Elimina un jugador de una partida o elimina toda la partida si el host decide abandonar antes de iniciar """
        
        # Obtener el jugador por su ID
        player = get_player(self.db, player_id)
        if not player:
            raise Exception("Jugador no encontrado")
        
        # Obtener la partida en la que está el jugador
        game = get_game_by_player_id(self.db, player_id)

        # Divide en si la partida no ha comenzado
        json_ws = {}
        game_id = game.id
        username = player.username
        if not game.started:
            # Si el jugador es el host
            if game.host == player:
                delete_all_game(self.db,game)
                json_ws = {"event": "game.cancelled", "payload": {"game_id": game_id}}
            else:
                # Si el jugador NO es el host
                delete_player_lobby(self.db, player, game)
                json_ws = {"event": "player.left", "payload": {"game_id": game_id, "username": username}}
            
            # Enviar evento websocket
            await manager.broadcast(json.dumps(json_ws), game_id)
            await manager.broadcast(json.dumps(json_ws), 0)

        else:
            # Si la partida ya ha comenzado y es justo turno del que abandona devuelve error si quedan mas de dos jugadores
            if player.turn == game.turn and len(game.players) > 2:
                raise Exception("No puede abandonar el jugador de turno")
            delete_player_game(self.db, player, game)

            json_ws = {"event": "player.left", "payload": {"game_id": game_id, "username": username}}
            await manager.broadcast(json.dumps(json_ws), game_id)
            
            #Checkea si queda solo un jugador
            if len(game.players) == 1:
                player_id = game.players[0].id
                delete_all_game(self.db,game)
                json_ws = {"event": "game.winner", "payload": {"player_id": player_id,}}
                await manager.broadcast(json.dumps(json_ws), game_id)
            

    async def create_game(self, game_data: CreateGame) -> PlayerAndGame:
        """ Crea una partida """
        if not game_data.player_name:
            raise Exception("El jugador debe tener un nombre")
        elif not game_data.game_name:
            raise Exception("La partida debe tener un nombre")
        game = create_game(self.db, game_data.game_name, game_data.password)
        player = create_player(self.db, game_data.player_name, game)
        game.host = player
        self.db.commit()
        json_ws = {"event": "game.new", "payload": {"game_id": game.id, "name": game.name, "players": len(game.players)}}
        await manager.broadcast(json.dumps(json_ws), 0)
        return PlayerAndGame(player_id=player.id, game_id=game.id)
   

    async def join_game(self, data: JoinGame) -> PlayerAndGame:
        """ Un jugador se une a una partida """
        if not data.player_name:
            raise Exception("El jugador debe tener un nombre")
        
        game = get_game(self.db, data.game_id)

        if game == None:
            raise Exception("Partida no encontrada")
        elif game.started:
            raise Exception("Partida ya iniciada")
        elif game.password and game.password != "":
            if game.password != data.password:
                raise Exception("Contraseña incorrecta")
        if len(game.players) >= 4:
            raise Exception("Partida con máximo de jugadores permitidos")
        player = create_player(self.db, data.player_name, game)

        json_ws = {"event": "player.new", "payload": {"game_id": game.id, "username": player.username}}
        await manager.broadcast(json.dumps(json_ws), game.id)
        await manager.broadcast(json.dumps(json_ws), 0)

        return PlayerAndGame(player_id=player.id, game_id=game.id)
    

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
        print("Se cambia el turno del jugador ", player_id)
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
        
        # Verificar si es el turno del jugador
        if player.turn == game.turn:
            #Cancela movimientos parciales si existen
            if parcial_movements_exist(game):
                move_service = MoveService(self.db)
                await move_service.revert_moves(PlayerAndGame(player_id=player_id,game_id=game.id))

            #Restablece cartas de movimientos si le faltan
            len_cards = len(get_moves_hand(self.db,player))
            if len_cards < 3:
                deck = get_moves_deck(self.db,game)
                #Si necesita mas de las que hay en el deck se reinicia el deck
                if (3-len_cards) > len(deck):
                    reset_moves_deck(self.db,game)
                    deck = get_moves_deck(self.db,game)
                #Asigno cartas de movimiento
                for _ in range(3-len_cards):
                    move = random.choice(deck)
                    deck.remove(move)
                    put_asign_movement(self.db, move, player)

            #Restablece cartas de figura si le faltan (si es que no esta bloqueado)
            if not has_blocked_figures(self.db, player):
                len_cards = len(get_figures_hand(self.db,player))
                if len_cards < 3:
                    figures = []
                    #Me fijo si puede obtener todas las cartas que necesita u obtiene todas directamente
                    deck = get_figures_deck(self.db,player)
                    if (3-len_cards) > len(deck):
                        for figure in deck: 
                            put_status_figure(self.db, figure, FigureStatus.INHAND)
                            figures.append(FigureOut(player_id=player_id, id_figure=figure.id, type_figure=figure.type.value))
                    else:
                        for _ in range(3-len_cards):
                            figure = random.choice(deck)
                            deck.remove(figure)
                            put_status_figure(self.db, figure, FigureStatus.INHAND)
                            figures.append(FigureOut(player_id=player_id, id_figure=figure.id, type_figure=figure.type.value))
                
                    if figures != []:
                        json_ws = {"event": "figure.card.added", "payload": [figure.model_dump() for figure in figures]}
                        await manager.broadcast(json.dumps(json_ws), game.id)

            # Actualizar el turno del juego
            update_turn_game(self.db, game)
            
        else:
            raise Exception("No es turno del jugador")
        
        json_ws = {"event": "game.turn", "payload": {"turn": game.turn}}
        await manager.broadcast(json.dumps(json_ws), game.id)