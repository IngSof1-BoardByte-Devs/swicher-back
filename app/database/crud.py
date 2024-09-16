"""
Este archivo se encarga de manejar todas las operaciones CRUD (Crear, Leer, Actualizar y Eliminar) sobre 
los modelos definidos. Aquí es donde implementas las funciones que interactúan con los datos a través de 
sesiones controladas de la base de datos.
"""

from pony.orm import db_session
from app.database.models import Player, Game


@db_session
def create_game(name: str) -> Game:
    new_game = Game(name=name)
    return new_game

@db_session
def create_player(username: str, game: Game) -> Player:
    new_player = Player(username=username, game=game)
    return new_player

@db_session
def fetch_games():
    return Game.select()

@db_session
def put_host(game: Game, player: Player):
    game.host = player


""" 
Usar @db_session cuando toda la función realiza operaciones con la base de datos, simplificando la gestión 
de la sesión.
Usar with db_session cuando solo una parte de la función necesita acceder a la base de datos o cuando tienes 
lógica compleja y necesitas más control sobre el manejo de la sesión. 
"""