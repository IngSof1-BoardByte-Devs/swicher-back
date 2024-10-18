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

        # Guardar la matriz en la base de datos
        update_board(self.db, game, matrix)
        

    def get_board_values(self, id_game: int) -> List[Color]:
        game = get_game(self.db, id_game)
        if not game:
            raise Exception("Partida no encontrada")
        elif not game.started:
            raise Exception("Partida no iniciada")
        matrix = game.board_matrix
        board_values = []
        for i in range(36):
            board_values.append(Color(color=matrix[i]))

        return BoardOut(board=board_values)