from app.database.crud import *
from app.schemas.movement import *
from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
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

    def get_movements(self, player_id: int):
            player = get_player(self.db,player_id)
            game = get_game_by_player_id(self.db,player_id)

            if not player:
                raise Exception("Jugador no encontrado")
            
            if not game.started:
                raise Exception("Partida no iniciada")

            return [MovementOut(id_movement = m.id, type_movement=m.type) for m in player.movements]
    
    def set_parcial_movement(self, id_player, id_move: int, x1: int, x2: int, y1: int, y2:int ) -> Movement:
        move = get_movement(self.db, id_move)
        if not move:
            raise Exception("La carta de movimiento no existe")
        
        game = move.game
        player = get_player(self.db, id_player)
        if game.turn != player.turn:
            raise Exception("No es tu turno")

        if move.status != MovementStatus.INHAND or move.player.id != id_player:
            raise Exception("La carta no te pertenece")

        if not self.validate_movement(id_move, x1, x2, y1, y2 ):
            raise Exception("La carta no es válida para ese movimiento")

        update_parcial_movement(self.db, game, move, x1, x2, y1, y2)

        return Movement(card_id = move.id, id_player = id_player, type = move.type)
        
    
    def validate_movement(self, id_move: int, x1: int, x2: int, y1: int, y2:int ) -> bool:
        move = get_movement(self.db, id_move)
        if not move:
            raise Exception("La carta de movimiento no existe")
        
        valid_moves = ValidMoves[str(move.type).replace("MovementType.", "")].value

        for dx, dy in valid_moves:
            print(x1, y1, x2, y2, dx, dy)
            if x1 == y1 + dx and x2 == y2 + dy: return True
        
        return False