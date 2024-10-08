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
            
            game = get_game_by_player_id(self.db,id)
            if not game.started:
                raise Exception("Partida no iniciada")

            return [MovementOut(id_movement = m.id, type_movement=m.type) for m in player.movements]
    
    def set_parcial_movement(self, id_player, id_move: int, x1: int, x2: int, y1: int, y2:int ) -> Movement:
        move = get_movement(self.db, id_move)
        if not move:
            raise Exception("La carta de movimiento no existe")
        game = move.game

        if move.player.id != id_player:
            raise Exception("La carta no te pertenece")

        """ if not self.validate_movement(id_move, x1, x2, y1, y2 ):
            raise Exception("Movimiento no válido") """

        update_parcial_movement(self.db, move, x1, x2, y1, y2)

        return move
        
    
    """ def validate_movement(self, id_move: int, x1: int, x2: int, y1: int, y2:int ) -> bool:
        move = get_movement(self.db, id_move)
        if not move:
            raise HTTPException(status_code=404, error="the movement card doesn't exist")
        game = move.game

        if game.turn != move.player.turn:
            raise HTTPException(status_code=404, error="It's not your turn")
        
        valid_moves = ValidMoves[move.type].value

        for dx, dy in valid_moves:
            if x1 == y1 + dx and x2 == y2 + dy: return True

        return False """