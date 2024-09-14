"""
Acá se definen las entidades o modelos de la base de datos, es decir, las tablas y sus relaciones. 
Se utiliza la instancia db creada en session.py para asociar las entidades a la base de datos.
"""

from pony.orm import Required, Set
from app.database.session import db

# Los nombre tienen que comenzar con mayúscula (salta error si no)
class Player(db.Entity):
    username = Required(str)
    mensaje = Set("Mensaje")

class Mensaje(db.Entity):
    mensaje = Required(str)
    player = Required(Player)
