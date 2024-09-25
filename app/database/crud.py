"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from sqlalchemy.orm import Session
from app.database.models import Player, Game

def create_game(db: Session, name: str) -> Game:
    new_game = Game(name=name)
    db.add(new_game)
    db.commit()
    return new_game

def create_player(db: Session, username: str, game: Game) -> Player:
    new_player = Player(username=username, game=game)
    db.add(new_player)
    db.commit()
    return new_player

def fetch_games(db: Session):
    return db.query(Game).all()

def put_host(db: Session, game: Game, player: Player):
    game.host = player
    db.commit()

def get_game(db: Session, id: int) -> Game:
    return db.query(Game).get(id)

def count_players(db: Session, game: Game) -> int:
    return db.query(Player).filter(Player.game_id == game.id).count()