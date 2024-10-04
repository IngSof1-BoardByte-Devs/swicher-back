from app.database.crud import *
from app.schemas.figure import FigureOut
from app.schemas.game import *

from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
import random

class FigureService:
    def __init__(self, db: Session):
        self.db = db

    def create_figure_deck(self, game_id: int) -> Dict:
        game = get_game(self.db, game_id)
        deck = []

        # Agrego las figuras simples al mazo
        easyTypes = [member for name, member in FigureType.__members__.items() if name.startswith('ETYPE')]
        for i in range(len(game.players) * 7):
            figure_type = random.choice(easyTypes)
            figure = new_figure(self.db, figure_type, game)
            deck.append(figure)

        # Agrego las figuras complejas al mazo
        complexTypes = list(member for name, member in FigureType.__members__.items() if name.startswith('TYPE'))
        for i in range(len(game.players) * 18):
            figure_type = random.choice(complexTypes)
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

    def get_figures(self, game_id: int):
        game = get_game(self.db, game_id)
        if game is None:
            HTTPException(status_code=404, detail="Game not found")
        
        figures = []
        for p in game.players:
            for m in p.figures:
                if m.status == FigureStatus.INHAND:
                    figures.append(FigureOut(player_id=p.id, id_figure=m.id, type_figure=m.type))

        return figures