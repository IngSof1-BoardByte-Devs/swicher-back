from app.database.crud import *
from app.schemas.game import PlayerAndGame
from app.schemas.movement import *
from typing import Dict, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
import random
from app.core.websocket import manager

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

            for mov in player.movements:
                print(f"Carta del jugador {player.username}: id={mov.id} y estado={mov.status.value}")
            return [MovementOut(id_movement = m.id, type_movement=m.type) for m in player.movements]
    
    async def set_parcial_movement(self, id_player, id_move: int, index1:int, index2:int) -> Movement:
        x1 = index1 // 6
        x2 = index1 % 6
        y1 = index2 // 6
        y2 = index2 % 6
        move = get_movement(self.db, id_move)
        if not move:
            raise Exception("La carta de movimiento no existe")
        
        game = move.game
        player = get_player(self.db, id_player)

        if not player:
            raise Exception("Jugador no encontrado")
        if game.turn != player.turn:
            raise Exception("No es tu turno")

        if move.status != MovementStatus.INHAND or move.player.id != id_player:
            raise Exception("La carta no te pertenece")

        if not self.validate_movement(id_move, x1, x2, y1, y2 ):
            raise Exception("La carta no es válida para ese movimiento")

        update_parcial_movement(self.db, game, move, x1, x2, y1, y2)
        swap_board(self.db, game, x1, x2, y1, y2)

        json_ws = {"event": "movement.card.used", "payload": {"card_id": move.id,"position1": index1,"position2": index2,"type":move.type.value}}
        await manager.broadcast(json.dumps(json_ws), game.id)

        return Movement(card_id = move.id, id_player = id_player, type = move.type)
        
    
    def validate_movement(self, id_move: int, x1: int, x2: int, y1: int, y2:int ) -> bool:
        move = get_movement(self.db, id_move)
        if not move:
            raise Exception("La carta de movimiento no existe")
        
        valid_moves = ValidMoves[str(move.type).replace("MovementType.", "")].value

        for dx, dy in valid_moves:
            if x1 == y1 + dx and x2 == y2 + dy: return True
        
        return False
    
    
    async def revert_moves(self, data: PlayerAndGame):
        game = get_game(self.db, data.game_id)
        if not game:
            raise Exception("Partida no encontrada")
        if not game.started:
            raise Exception("Partida no iniciada")
        if not parcial_movements_exist(game):
            raise Exception("No hay cambios para revertir")
        
        player = get_player(self.db, data.player_id)
        if not player:
            raise Exception("Jugador no encontrado")
        if player not in game.players:
            raise Exception("El jugador no pertenece a esta partida")
        if player.turn != game.turn:
            raise Exception("No tienes autorización para revertir estos cambios")
        
        moves = []
        for mov in reversed(game.partial_movements):
            index1 = mov.x1 * 6 + mov.x2
            index2 = mov.y1 * 6 + mov.y2
            moves.append({"card_id": mov.movement_id,"position1": index1,"position2": index2})
            swap_board(self.db, game, mov.x1, mov.x2, mov.y1, mov.y2)
        
        revert_partial_movements(self.db, game, player)

        json_ws = {"event": "moves.cancelled", "payload": moves}
        await manager.broadcast(json.dumps(json_ws), game.id)