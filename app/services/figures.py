from app.database.crud import *
from app.schemas.figure import FigUpdate, FigureOut
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
        if not game:
            raise Exception("Partida no encontrada")
        if not game.started:
            raise Exception("Partida no iniciada")
        
        figures = []
        for p in game.players:
            for m in p.figures:
                if m.status == FigureStatus.INHAND:
                    figures.append(FigureOut(player_id=p.id, id_figure=m.id, type_figure=m.type))

        return figures
    
    def update_figure_service_status(self, figure_id: int, player_id: int, new_status: FigureStatus) -> FigUpdate:
        # Obtenemos la figura por su ID
        figure = get_figure_by_id(self.db, figure_id)
        if not figure:
            raise Exception("La carta de figura no existe")

        # Verificamos si la carta pertenece al jugador
        if figure.player is None or figure.player.id != player_id:
            raise Exception("La carta no te pertenece")

        # Verificamos si la partida ha comenzado
        game = figure.game
        if not game.started:
            raise Exception("La partida no ha comenzado")
        
        # Verificamos que sea el turno del jugador
        if game.turn != player_id:
            raise Exception("No es tu turno")
        
        # Capturamos el ID del jugador antes de modificar la carta
        current_player_id = figure.player.id
        
        # Actualizamos el estado de la figura en la base de datos
        updated_figure = update_figure_status(self.db, figure, new_status)
        # Si la figura fue descartada, eliminamos los movimientos parciales asociados
        
        if new_status == FigureStatus.DISCARDED:

            # Eliminamos los movimientos parciales asociados a la partida
            delete_partial_movements(self.db, game)
            
            # Desvinculamos al jugador de la figura en la base de datos
            remove_player_from_figure(self.db, figure)
    
        return self.prepare_figure_update_response(updated_figure, current_player_id)

