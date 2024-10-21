from app.database.crud import *
from app.schemas.figure import FigUpdate, FigureOut
from app.schemas.game import *
from app.core.websocket import manager

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
    
    async def discard_figure(self,figure: Figure, player: Player, game: Game):
        # Elimino la figura
        delete_figure(self.db, figure)
        
        # Verificar si el jugador ha descartado todas sus cartas de figura
        remaining_figures = get_figures_hand(self.db, player).extend(get_figures_deck(self.db, player))
        if len(remaining_figures) == 0:
            # Si no quedan más cartas en la mano, el jugador gana
            player_id = player.id
            game_id = game.id
            delete_all_game(self.db, game)
            json_ws = { "event": "game.winner", "payload": { player_id: player_id }}
            await manager.broadcast(json.dumps(json_ws), game_id)
        
        # Elimino movimientos parciales
        delete_partial_movements(self.db, game)

    
    async def update_figure_service_status(self, figure_id: int, player_id: int) -> FigUpdate:
        figure = get_figure(self.db, figure_id)
        if not figure:
            raise Exception("La carta de figura no existe")
        
        player = get_player(self.db, player_id)
        game = figure.game

        if player.game != game:
            raise Exception("La carta/jugador no pertenece a este juego")
        if figure.status != FigureStatus.INHAND:
            raise Exception("La carta debe estar en la mano")
        if game.turn != player.turn:
            raise Exception("No es tu turno")
        
        blocked = figure.player.id != player_id

        updatefig = FigUpdate(id = figure.id,
                              id_player = player.id,
                              type = figure.type,
                              discarded = not blocked,
                              blocked = blocked)

        if blocked:
            #Funcion para bloquear figura (NO IMPLEMENTADO EN ESTE SPRINT)
            raise Exception("Función de bloquear figura no implementada")
        else:
            #Funcion para descartar figura propia
            await self.discard_figure(figure,player,game)
        
        json_ws = { "event": "figure.card.used",
                   "payload": { "card_id": figure_id,"discarded": not blocked,
                                "locked": blocked}}
        await manager.broadcast(json.dumps(json_ws), game.id)
    
        return updatefig