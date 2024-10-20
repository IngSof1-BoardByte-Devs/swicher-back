"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from typing import List
from sqlalchemy.orm import Session
from app.database.models import *
from app.schemas.figure import FigUpdate
from app.utils.enums import *

def get_game(db: Session, game_id: int) -> Game:
    return db.query(Game).filter(Game.id == game_id).first()

def create_game(db: Session, name: str) -> Game:
    new_game = Game(name=name)
    db.add(new_game)
    db.commit()
    return new_game

def create_player(db: Session, username: str, game: Game) -> Player:
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
        db.delete(player)
        db.commit()

def delete_all_game(db: Session, game: Game):
    for movement in game.movements:
        db.delete(movement)
    for figure in game.figures:
        db.delete(figure)
    for player in game.players:
        db.delete(player)
    for partial_mov in game.partial_movements:
        db.delete(partial_mov)
    db.delete(game)
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
    return matrix

def get_player(db: Session, id: int) -> Player | None:
    return db.query(Player).get(id)

def get_players_in_game(db: Session, player_id: int):
    player = get_player(db, player_id)
    game = player.game
    return game.players

def update_turn_game(db : Session, game: Game):
    turn = (game.turn + 1) % (len(game.players) + 1)
    if turn == 0: turn = 1
    game.turn = turn
    db.commit()

def get_game_by_player_id(db: Session, player_id: int) -> Game:
    player = get_player(db, player_id)
    return player.game

def swap_board(db: Session, game: Game, x1: int, x2 : int, y1: int, y2: int):
    index1 = x1 * 6 + x2
    index2 = y1 * 6 + y2
    matrix = game.board_matrix
    temp = matrix[index1]
    matrix[index1] = matrix[index2]
    matrix[index2] = temp
    update_board(db, game, matrix)

def update_parcial_movement(db: Session, game: Game, movement: Movement, x1: int, x2: int, y1: int, y2: int):
    new_parcial_movements = PartialMovement(game_id=game.id, movement_id=movement.id, x1=x1, x2=x2, y1=y1, y2=y2)
    game.partial_movements.append(new_parcial_movements)
    movement.status = MovementStatus.DISCARDED
    player = movement.player
    player.movements.remove(movement)
    movement.player = None
    db.commit()

def get_movement(db: Session, movement_id: int) -> Movement:
    return db.query(Movement).get(movement_id)

def delete_partial_movements(db: Session, game: Game, player: Player):
    for _ in range(len(game.partial_movements)):
        mov = game.partial_movements[0].movement
        mov.player = player
        mov.status = MovementStatus.INHAND
        db.delete(game.partial_movements[0])
    db.commit()

def parcial_movements_exist(game: Game) -> bool:
    return len(game.partial_movements) != 0

def get_figure_by_id(db: Session, figure_id: int) -> Figure:
    return db.query(Figure).filter(Figure.id == figure_id).first()

def delete_partial_movements(db: Session, game: Game):
    for partial_movement in game.partial_movements:
        db.delete(partial_movement)
    db.commit()

def update_figure_status(db: Session, figure: Figure):
    db.commit()
    db.refresh(figure)  
    return figure

def remove_player_from_figure(db: Session, figure: Figure):
    figure.player = None
    db.commit()
    db.refresh(figure)  
    return figure

def prepare_figure_update_response(self, figure: Figure, current_player_id: int) -> FigUpdate:

    figu = FigUpdate(
            id=figure.id,
            id_player=current_player_id,
            type=figure.type,
            discarded=figure.discarded,
            blocked=figure.blocked
    )

    return figu