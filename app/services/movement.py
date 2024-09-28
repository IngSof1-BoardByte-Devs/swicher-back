from app.database.crud import *
from app.schemas.movement import *
from typing import Dict, List
from sqlalchemy.orm import Session
import random

class MoveService:
    def __init__(self, db: Session):
        self.db = db

    def create_movement_deck(self, game_id: int) -> Dict:
        game = get_game(self.db, game_id)
        deck = []

        # Creo un mazo de 36 movimientos
        types = list(MovementType.__members__.values())
        for i in range(36):
            movement_type = types[i % len(types)]
            movement = create_movement(self.db, game, movement_type)
            deck.append(movement)
        
        # Barajo el mazo
        random.shuffle(deck)

        # Asigno los movimientos a los jugadores
        for i in range(len(game.players)):
            player = game.players[i]
            for j in range(3):
                movement = deck.pop()
                put_asign_movement(self.db, movement, player)

    def get_movements(self, id: int):
            player = get_player(self.db,id)
            game = get_game_by_player_id(self.db,id)

            if not player:
                raise Exception("No existe jugador")

            if not game.started:
                raise Exception("La partida no está empezada")

            return [MovementOut(card_id = m.id, movement_type=m.type) for m in player.movements]