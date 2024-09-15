"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from pony.orm import db_session
from app.database.models import Game, Player

@db_session
def fetch_games():
    return Game.select()

""" 
Usar @db_session cuando toda la función realiza operaciones con la base de datos, simplificando la gestión 
de la sesión.
Usar with db_session cuando solo una parte de la función necesita acceder a la base de datos o cuando tienes 
lógica compleja y necesitas más control sobre el manejo de la sesión. 
"""