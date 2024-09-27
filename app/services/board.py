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

    def get_board(self, game_id: int) -> BoardState:
        game = get_game(self.db, game_id)
        matrix = game.board_matrix
        board = []
        for y, row in enumerate(matrix):
            for x, figure_id in enumerate(row):
                board.append(Figure(figure_id=figure_id, position=Position(x=x, y=y)))
        return BoardState(board_state=board)