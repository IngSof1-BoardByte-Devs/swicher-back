"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from sqlalchemy.orm import Session
from app.database.models import Player, Game

def get_game(db: Session, game_id: int) -> Game:
    print("Esto es dentro del crud get game, no debería ejecutarse en el test")
    return db.query(Game).filter(Game.id == game_id).first()

def create_game(db: Session, name: str) -> Game:
    print("Esto es dentro del crud para crear partida")
    new_game = Game(name=name)
    db.add(new_game)
    db.commit()
    return new_game

def create_player(db: Session, username: str, game: Game) -> Player:
    
    print("Esto es dentro del crud create player, no debería ejecutarse en el test")
    if not username or not game:
        raise ValueError("Invalid arguments")
    new_player = Player(username=username, game=game)
    db.add(new_player)
    db.flush()
    db.commit()
    return new_player

def fetch_games(db: Session):
    return db.query(Game).all()

def put_host(db: Session, game: Game, player: Player):
    game.host = player
    db.commit()