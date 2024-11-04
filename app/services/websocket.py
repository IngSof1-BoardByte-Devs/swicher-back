#Handle generic websocket data
from fastapi import WebSocket
from app.websocket_manager import ConnectionManager
from app.services.game import GameService
from app.services.board import BoardService
from app.services.player import PlayerService
from app.services.movement import MoveService
from app.services.figures import FigureService
import json

manager = ConnectionManager()

async def handle_event(websocket: WebSocket, data: str):
    game_service = GameService()
    board_service = BoardService()
    player_service = PlayerService()
    movement_service = MoveService()
    figure_service = FigureService()
    
    try:
        # Events de Game
        if data.startswith("games.fetch"):
            json = game_service.get_all_games()
            await manager.send_personal_message(json.dumps(json), websocket)
            
        elif data.startswith("board.fetch"):
            game_id = int(data.split(" ", 1)[1])
            json = await board_service.get_board_values(game_id)
            await manager.send_personal_message(json.dumps(json), websocket)

        # Events de Player
        elif data.startswith("players.fetch"):
            game_id = int(data.split(" ", 1)[1])
            json = player_service.get_players(game_id)
            await manager.send_personal_message(json.dumps(json), websocket)

        # Events de Movement
        elif data.startswith("movement-cards.fetch"):
            game_id = int(data.split(" ", 1)[1])
            json = movement_service.get_movements(game_id)
            await manager.send_personal_message(json.dumps(json), websocket)

        # Events de Figure
        elif data.startswith("figure-cards.fetch"):
            game_id = int(data.split(" ", 1)[1])
            json = figure_service.get_figures(game_id)
            await manager.send_personal_message(json.dumps(json), websocket)
                    

    except Exception as e:
        await manager.broadcast("Error", 0)