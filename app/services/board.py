from app.database.crud import *
from app.schemas.game import *
from app.schemas.board import *
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
        
        # Crear la matriz 6x6
        matrix = [[deck.pop() for _ in range(6)] for _ in range(6)]

        # Guardar la matriz en la base de datos
        update_board(self.db, game, matrix)

    def get_board_values(self, player_id: int) -> List[Color]:
        game = get_game_by_player_id(self.db, player_id)
        matrix = game.board_matrix
        board_values = []
        color = Color
        # Guardar todo como una lista de enteros
        for i in range(6):
            for j in range(6):
                board_values.append(Color(color = matrix[i][j]))

        return BoardOut(board= board_values)