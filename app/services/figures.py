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
                
    async def get_figures(self, game_id: int):
        game = get_game(self.db, game_id)
        if not game:
            raise Exception("Partida no encontrada")
        if not game.started:
            raise Exception("Partida no iniciada")
        
        figures = []
        payload = []
        for p in game.players:
            for m in p.figures:
                if m.status == FigureStatus.INHAND or m.status == FigureStatus.BLOCKED:
                    figures.append(FigureOut(player_id=p.id, id_figure=m.id, type_figure=m.type, locked=(m.status==FigureStatus.BLOCKED)))
            payload.append({"player_id": p.id, "deck": len(get_figures_deck(self.db,p))})
        
        json_ws = { "event": "figure.card.deck", "payload": payload}
        await manager.broadcast(json.dumps(json_ws), game_id)
        return figures
    
    async def discard_figure(self,figure: Figure, player: Player, game: Game):
        if figure.status == FigureStatus.BLOCKED and len(get_figures_hand(self.db,player)) != 0:
            raise Exception("El jugador no puede descartar una carta bloqueada")
        # Elimino la figura
        delete_figure(self.db, figure)
        
        # Verificar si el jugador ha descartado todas sus cartas de figura
        remaining_figures = get_figures_hand(self.db,player) + (get_figures_deck(self.db, player))
        if len(remaining_figures) == 0 and not has_blocked_figures(self.db,player):
            # Si no quedan más cartas en la mano, el jugador gana
            player_id = player.id
            game_id = game.id
            delete_all_game(self.db, game)
            json_ws = { "event": "game.winner", "payload": { "player_id": player_id }}
            await manager.broadcast(json.dumps(json_ws), game_id)

    def block_figure(self, figure: Figure):
        player = figure.player
        if has_blocked_figures(self.db, player):
            raise Exception("El jugador ya tiene una carta bloqueada")
        elif len(get_figures_hand(self.db, player)) < 2:
            raise Exception("El jugador debe tener mas de dos cartas para ser bloqueado")
        block_figure_status(self.db,figure)
        #print(f"Bloqueo la figura del jugador {player.username}")

    
    async def update_figure_status(self, figure_id: int, player_id: int, color: int) -> FigUpdate:
        figure = get_figure(self.db, figure_id)
        if not figure:
            raise Exception("La carta de figura no existe")
        
        player = get_player(self.db, player_id)
        game = figure.game

        #print(f"El jugador {player.username} selecciona la figura del jugador {figure.player.username}")
        if player.game != game:
            raise Exception("La carta/jugador no pertenece a este juego")
        if figure.status == FigureStatus.INDECK:
            raise Exception("La carta debe estar en la mano")
        if game.turn != player.turn:
            raise Exception("No es tu turno")
        if game.bloqued_color == color:
            raise Exception("La figura es del color prohibido")
        if color > 3 or color < 0:
            raise Exception("Color inválido")

        blocked = figure.player.id != player_id

        updatefig = FigUpdate(id = figure.id,
                              id_player = player.id,
                              type = figure.type,
                              discarded = not blocked,
                              blocked = blocked)
        
        
        hand_figures = get_figures_hand(self.db, player)
        hand_fig_block = has_blocked_figures(self.db, player)

        if hand_fig_block and len(hand_figures) == 0:
            json_ws = {
                "event": "figure.card.unlocked",
                "payload": {
                    "card_id": figure_id,
                    "player_id": player_id
                }
            }
            # #check consola ws
            # print("WebSocket message prepared:", json.dumps(json_ws))
            await manager.broadcast(json.dumps(json_ws), game.id)
                

        if blocked:
            #Funcion para bloquear figura 
            self.block_figure(figure)
            json_action_event = {"event": "message.action", "payload": {"message": f"{player.username} ha bloqueado una figura de {figure.player.username}"}}
            await manager.broadcast(json.dumps(json_action_event), game.id)
        else:
            #Funcion para descartar figura propia
            await self.discard_figure(figure,player,game)
            json_action_event = {"event": "message.action", "payload": {"message": f"{player.username} ha reconocido una figura"}}
            await manager.broadcast(json.dumps(json_action_event), game.id)
        
        update_color(self.db, game, color)

        # Elimino movimientos parciales
        delete_partial_movements(self.db, game, player)
        
        json_ws = { "event": "figure.card.used",
                   "payload": { "card_id": figure_id,"discarded": not blocked,
                                "locked": blocked, "color": color}}
        await manager.broadcast(json.dumps(json_ws), game.id)
    
        return updatefig