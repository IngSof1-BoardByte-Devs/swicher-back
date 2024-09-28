"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from typing import List
from sqlalchemy.orm import Session
from app.database.models import *
from app.utils.enums import *
import enum

def get_game(db: Session, game_id: int) -> Game:
    return db.query(Game).filter(Game.id == game_id).first()

def create_game(db: Session, name: str) -> Game:
    new_game = Game(name=name)
    db.add(new_game)
    db.commit()
    return new_game

def create_player(db: Session, username: str, game: Game) -> Player:
    if not username or not game:
        raise ValueError("Invalid arguments")
    new_player = Player(username=username, game=game)
    db.add(new_player)
    db.flush()
    db.commit()
    return new_player

def fetch_games(db: Session):
    return db.query(Game)

def put_host(db: Session, game: Game, player: Player):
    game.host = player
    db.commit()

def delete_player(db: Session, player: Player, game: Game):
    if not game.started:
        raise Exception("Cannot leave game that has started")
    else:
        game.players.remove(player)
        player.delete()
        db.commit()

def delete_all_game(db: Session, game: Game):
    for movement in game.movements:
        movement.delete()
    for figure in game.figures:
        figure.delete()
    for player in game.players:
        player.delete()
    game.delete()
    db.commit()

def get_player_by_id(db: Session, player_id: int):
    return db.query(Player).filter(Player.id == player_id).first()

def get_game_by_id(db: Session, game_id: int):
    return db.query(Game).filter(Game.id == game_id).first()

def create_movement(db: Session, game: Game, type: Enum):
    new_movement = Movement(type=type, game=game)
    db.add(new_movement)
    db.commit()
    return new_movement

def new_figure(db: Session, type: Enum, game: Game):
    new_figure = Figure(type=type, game=game)
    db.add(new_figure)
    db.commit()
    return new_figure

def put_start_game(db: Session, game: Game):
    game.started = True
    game.turn = 1
    db.commit()

def put_asign_movement(db: Session, movement: Movement, player: Player):
    movement.player = player
    movement.status = MovementStatus.INHAND
    db.commit()

def put_asign_figure(db: Session, figure: Figure, player: Player):
    figure.player = player
    db.commit()

def put_status_figure(db: Session, figure: Figure, status: FigureStatus):
    figure.status = status
    db.commit()

def put_status_movement(db: Session, movement: Movement, status: MovementStatus):
    movement.status = status
    db.commit()

def put_asign_turn(db: Session, player: Player, turn: int):
    player.turn = turn
    db.commit()

def update_board(db: Session, game: Game, matrix: list):
    game.board_matrix = matrix
    db.commit()
    return game

def get_player(db: Session, id: int) -> Player | None:
    return db.query(Player).get(id)

def get_players_in_game(db: Session, player_id: int):
    player = get_player(db, player_id)
    game = player.game
    return game.players

def update_turn_game(db : Session, game: Game):
    game.turn = ((game.turn + 1) % len(game.players)) + 1

def get_game_by_player_id(db: Session, player_id: int) -> Game:
    return get_player(db,id).game
    