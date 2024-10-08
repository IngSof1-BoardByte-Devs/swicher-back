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
        easy_deck = []
        complex_deck = []

        # Agrego las figuras fáciles al mazo
        easyTypes = [member for name, member in FigureType.__members__.items() if 19 <= int(name[4:]) <= 25]
        for i in range(14):
            figure_type = easyTypes[i % len(easyTypes)]
            figure = new_figure(self.db, figure_type, game)
            easy_deck.append(figure)

        # Agrego las figuras complejas al mazo
        complexTypes = [member for name, member in FigureType.__members__.items() if 1 <= int(name[4:]) <= 18]
        for i in range(36):
            figure_type = complexTypes[i % len(complexTypes)]
            figure = new_figure(self.db, figure_type, game)
            complex_deck.append(figure)
        
        # Barajo el mazo
        random.shuffle(easy_deck)
        random.shuffle(complex_deck)

        # Asigno las figuras fáciles a los jugadores
        for j in range(14 // len(game.players)):
            for i in range(len(game.players)):
                player = game.players[i]
                figure = random.choice(easy_deck)
                easy_deck.remove(figure)
                put_asign_figure(self.db, figure, player)
        
        # Asigno las figuras complejas a los jugadores
        for j in range(36 // len(game.players)):
            for i in range(len(game.players)):
                player = game.players[i]
                figure = random.choice(complex_deck)
                complex_deck.remove(figure)
                put_asign_figure(self.db, figure, player)
        
        
        # Asigno las figuras que van a iniciar en juego
        for i in range(len(game.players)):
            player = game.players[i]
            # Selecciona 3 figuras únicas del jugador
            selected_figures = random.sample(player.figures, 3)
            for figure in selected_figures:
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