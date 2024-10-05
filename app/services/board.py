from app.database.crud import *
from app.schemas.game import *
from app.schemas.board import *
from app.schemas.movement import *
from app.services.movement import *
from typing import Dict, List
from sqlalchemy.orm import Session
import random

class BoardService:
    def __init__(self, db: Session):
        self.db = db

    def create_board(self, game_id: int):
        game = get_game(self.db, game_id)
        
        # Crear el mazo de 36 elementos (4 tipos, 9 cartas cada uno)
        deck = [i for i in range(4) for _ in range(9)]
        random.shuffle(deck)
        
        # Crear la matriz como array de 36 elementos
        matrix = [deck[i] for i in range(36)]
        for i in range(36):
            print("llega acá " + str(matrix[i]))

        # Guardar la matriz en la base de datos
        update_board(self.db, game, matrix)
        

    def get_board_values(self, id_game: int) -> List[Color]:
        print("llega acá 3")
        game = get_game(self.db, id_game)
        matrix = game.board_matrix
        board_values = []
        for i in range(36):
            print("llega acá " + str(i) + ": " + str(matrix[i]))
        for i in range(36):
            print("llega acá 3.1")
            board_values.append(Color(color=matrix[i]))

        print("llega acá 4")
        return BoardOut(board=board_values)
    

    def switch_values(self, game: Game, x: int, y: int) -> List[int]:
        matrix = game.board_matrix
        valorSwitch = matrix[x]
        matrix[x] = matrix[y]
        matrix[y] = valorSwitch
        # Guardar la matriz en la base de datos
        update_board(self.db, game, matrix)
        return matrix
    
    def switch_values(self, id_move: int, x: int, y: int) -> Movement:
        game = get_game_by_move_id(self.db, id_move)

        # Guardar el movimiento parcial
        move = MoveService
        movement = move.set_parcial_movement(self.db, id_move, x, y)

        # Cambiar los valores de la matriz
        matrix = self.switch_values(game, x, y)

        # Guardar la matriz en la base de datos
        update_board(self.db, game, matrix)

        return MovementOut(id= movement.id, id_player= movement.id_player, type= movement.type)