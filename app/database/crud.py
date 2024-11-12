"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import exists
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

def delete_player_lobby(db: Session, player: Player, game: Game):
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
    player.movements.append(movement)
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

def revert_partial_movements(db: Session, game: Game, player: Player):
    cant = len(game.partial_movements)
    for _ in range(cant):
        partial = game.partial_movements[0]
        mov = partial.movement
        mov.player = player
        mov.status = MovementStatus.INHAND
        game.partial_movements.remove(partial)
        db.delete(partial)
    db.commit()

def delete_partial_movements(db: Session, game: Game, player: Player):
    cant = len(game.partial_movements)
    for _ in range(cant):
        partial = game.partial_movements[0]
        game.partial_movements.remove(partial)
        db.delete(partial)
    db.commit()

def parcial_movements_exist(game: Game) -> bool:
    return len(game.partial_movements) != 0
  

def get_figure(db: Session, figure_id: int) -> Figure:
    return db.query(Figure).filter(Figure.id == figure_id).first()

def delete_figure(db: Session, figure: Figure):
    figure.player.figures.remove(figure)
    db.delete(figure)
    db.commit()

def delete_player_game(db: Session, player: Player, game: Game):
    #Descartar cartas de movimiento
    for mov_card in player.movements:
        mov_card.status = MovementStatus.DISCARDED
        mov_card.player = None
    #Eliminar cartas de figura
    for fig_card in player.figures: db.delete(fig_card)
    #Actualizar turnos de los jugadores
    for p in game.players:
        if p.turn > player.turn:
            p.turn -= 1
    #Actualizo turno del juego si es necesario
    if game.turn > player.turn: game.turn -=  1
    #Pongo en None el host si es el host quien se va
    if game.host == player: game.host = None

    #Subo los cambios
    db.commit()
    #Elimino el jugador
    delete_player_lobby(db, player, game)

def get_moves_deck(db,game):
    movements_in_deck = db.query(Movement).filter(
        Movement.game == game,
        Movement.status == MovementStatus.INDECK
    ).all()
    return movements_in_deck

def get_moves_hand(db,player):
    moves_in_deck = db.query(Movement).filter(
        Movement.player == player,
        Movement.status == MovementStatus.INHAND
    ).all()
    return moves_in_deck

def reset_moves_deck(db,game):
    db.query(Movement).filter(
        Movement.game == game, 
        Movement.status == MovementStatus.DISCARDED
    ).update({"status": MovementStatus.INDECK})
    db.commit()

def get_figures_hand(db,player):
    figures_in_hand = db.query(Figure).filter(
        Figure.player == player,
        Figure.status == FigureStatus.INHAND
    ).all()
    return figures_in_hand

def has_blocked_figures(db, player):
    figures_blocked = db.query(Figure).filter(
        Figure.player == player,
        Figure.status == FigureStatus.BLOCKED
    ).all()
    return figures_blocked != []

def get_figures_hand(db,player):
    figures_in_hand = db.query(Figure).filter(
        Figure.player == player,
        Figure.status == FigureStatus.INHAND
    ).all()
    return figures_in_hand
    
def get_figures_hand_or_bloqued_game(db, game_id):
    figures_in_hand = db.query(Figure).filter(
        Figure.game_id == game_id,
        Figure.status.in_([FigureStatus.INHAND, FigureStatus.BLOCKED])
    ).all()
        
    return figures_in_hand

def get_blocked_figure(db: Session, player: Player) -> Figure | None:
    return db.query(Figure).filter(
        Figure.player == player,
        Figure.status == FigureStatus.BLOCKED
    ).first()

def get_figures_deck(db,player):
    figures_in_deck = db.query(Figure).filter(
        Figure.player == player,
        Figure.status == FigureStatus.INDECK
    ).all()
    return figures_in_deck

def update_color(db, game, color):
    game.bloqued_color = color
    db.commit()

def block_figure_status(db,figure):
    figure.status = FigureStatus.BLOCKED
    db.commit()