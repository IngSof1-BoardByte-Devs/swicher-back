#Handle generic websocket data
from fastapi import WebSocket, Depends
from app.websocket_manager import ConnectionManager
from sqlalchemy.orm import Session
from app.database.session import get_db
import json
import logging

manager = ConnectionManager()

async def handle_event(websocket: WebSocket, data: str):
    from app.services.game import GameService
    from app.services.board import BoardService
    from app.services.player import PlayerService
    from app.services.movement import MoveService
    from app.services.figures import FigureService

    db_gen = get_db()
    db: Session = next(db_gen)
    
    game_service = GameService(db)
    board_service = BoardService(db)
    player_service = PlayerService(db)
    movement_service = MoveService(db)
    figure_service = FigureService(db)
    
    try:
        # Events de Game
        if data.startswith("games.fetch"):
            games = game_service.get_all_games()
            logging.info("Fetched games successfully")
            await manager.send_personal_message(json.dumps(games), websocket)
            logging.info("Games fetched and sent")
                
        elif data.startswith("board.fetch"):
            game_id = int(data.split(" ", 1)[1])
            board_values = await board_service.get_board_values(game_id)
            await manager.send_personal_message(json.dumps(board_values), websocket)

        # Events de Player
        elif data.startswith("players.fetch"):
            game_id = int(data.split(" ", 1)[1])
            players = player_service.get_players(game_id)
            await manager.send_personal_message(json.dumps(players), websocket)

        # Events de Movement
        elif data.startswith("movement-cards.fetch"):
            game_id = int(data.split(" ", 1)[1])
            movements = movement_service.get_movements(game_id)
            await manager.send_personal_message(json.dumps(movements), websocket)

        # Events de Figure
        elif data.startswith("figure-cards.fetch"):
            game_id = int(data.split(" ", 1)[1])
            figures = figure_service.get_figures(game_id)
            await manager.send_personal_message(json.dumps(figures), websocket)

        # Invalid Event
        else:
            await manager.send_personal_message("Invalid command", websocket)
                    
    except Exception as e:
        logging.error(f"Error handling event: {e}")
        await manager.send_personal_message(json.dumps({"error": "Failed to handle event"}), websocket)
    finally:
        db.close()
        logging.info("Event handling completed")