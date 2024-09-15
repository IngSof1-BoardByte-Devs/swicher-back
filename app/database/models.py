"""
Acá se definen las entidades o modelos de la base de datos, es decir, las tablas y sus relaciones. 
Se utiliza la instancia db creada en session.py para asociar las entidades a la base de datos.
"""

from pony.orm import Required, Set, Optional
from app.database.session import db

# Los nombre tienen que comenzar con mayúscula (salta error si no)
class Game(db.Entity):
    name = Required(str)
    players = Set("Player", reverse="game")
    started = Required(bool, default=False)
    turn = Required(int, default=0)
    host = Optional("Player", reverse="host_game")
    
class Player(db.Entity):
    username = Required(str)
    game = Required(Game)
    host_game = Optional(Game)
    turn = Required(int, default=0)

""" class Mensaje(db.Entity):
    mensaje = Required(str) """
