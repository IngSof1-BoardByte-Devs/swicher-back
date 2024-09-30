from app.database.crud import *
from app.schemas.figure import FigureOut
from app.schemas.game import *

from typing import Dict, List
from sqlalchemy.orm import Session
import random

class FigureService:
    def __init__(self, db: Session):
        self.db = db

    def create_figure_deck(self, game_id: int) -> Dict:
        game = get_game(self.db, game_id)
        deck = []

        # Creo un mazo de 92 figuras
        types = list(FigureType.__members__.values())
        for i in range(92):
            figure_type = types[i % len(types)]
            figure = new_figure(self.db, figure_type, game)
            deck.append(figure)
        
        # Barajo el mazo
        random.shuffle(deck)

        # Asigno las figuras a los jugadores
        for i in range(len(game.players)):
            player = game.players[i]
            for j in range(23):
                figure = deck.pop()
                put_asign_figure(self.db, figure, player)
        
        # Asigno las figuras que van a iniciar en juego
        for i in range(len(game.players)):
            player = game.players[i]
            for j in range(3):  # Cantidad de figuras sobre la mesa (no me acuerdo cuantas son)
                figure = player.figures[j]
                put_status_figure(self.db, figure, FigureStatus.INHAND)

    def get_figures(self, id: int):
        player = get_player(self.db, id)
        if player is None:
            raise Exception("No existe jugador")
        if player.game.started != True:
            raise Exception("El juego no ha comenzado")
        if not player:
            raise Exception("No existe jugador")
        
        figures = []
        for p in player.game.players:
            for m in p.figures:
                if m.status == FigureStatus.INHAND:
                    figures.append(FigureOut(player_id=p.id, id_figure=m.id, type_figure=m.type))

        return figures