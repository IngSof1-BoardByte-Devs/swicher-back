from app.database.crud import *
from app.schemas.game import *
from app.schemas.board import *
from app.schemas.figure import *
from app.schemas.movement import *
from app.services.movement import *
from app.utils.dict import *
from app.core.websocket import manager
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
        
        self.get_figures_from_board(game.id)

        return BoardOut(board=board_values)
    

    def get_valid_figures(self, array):
        '''
            Función que retorna una lista de figuras y sus índices originales
        '''
        figures = []
        for i in range(36):
            if any(figure[0][i] for figure in figures):
                continue
            figure, indices = self.dfs_iter(i, array)
            # Si la figura tiene 4 o 5 casillas, se agrega a la lista de figuras
            if 4 <= figure.count(True) < 6:
                figures.append((figure, indices))
        return figures


    def dfs_iter(self, s, array):
        '''
            Función que retorna una figura y sus índices originales dado un punto de inicio
        '''
        figure = [False] * 36 # Inicializar todos los vértices como no figura
        indices = []  # Lista para almacenar los índices originales

        # Inicializar la pila con la casilla inicial
        stack = [s]
        while stack:
            v = stack.pop()
            if figure[v]:   # Si ya se agregó a la figura, se salta a la siguiente iteración
                continue    
            figure[v] = True
            indices.append(v)  # Agregar el índice original
            x, y = v % 6, v // 6  # Coordenadas x e y de la celda actual
            candidates = []
            if x > 0: candidates.append(v - 1)  # Celda a la izquierda
            if x < 5: candidates.append(v + 1)  # Celda a la derecha
            if y > 0: candidates.append(v - 6)  # Celda arriba
            if y < 5: candidates.append(v + 6)  # Celda abajo
            for i in candidates:
                if array[i] == array[v]:  # Si la casilla es válida y tiene el mismo número
                    stack.append(i)

        return figure, indices


    def normalize_figures(self, figures):
        '''
            Función que normaliza las figuras (moverlas a la esquina superior izquierda)
        '''
        valid_figures = []  # Lista para almacenar las figuras válidas
        for figure, indices in figures:
            min_x = min(i % 6 for i, val in enumerate(figure) if val)
            min_y = min(i // 6 for i, val in enumerate(figure) if val)
            new_figure = [False] * 36
            for i in range(36):
                if figure[i]:
                    x = i % 6
                    y = i // 6
                    new_figure[(x - min_x) + 6 * (y - min_y)] = True
            valid_figures.append((new_figure, indices))
        return valid_figures


    def array_to_int(self, array):
        '''
            Función que convierte un array a un entero
        '''
        max_col = max_row = 0
        for i in range(len(array)):
            if array[i]:
                max_col = max(max_col, i % 6)
                max_row = max(max_row, i // 6)
        figure = str(max_row+1) + str(max_col+1)  # Agrega max_row y max_col al principio
        for i in range(max_row + 1):  # Cambiado a max_row + 1
            for j in range(max_col + 1):  # Cambiado a max_col + 1
                if array[i * 6 + j]:
                    figure += '1'
                else:
                    figure += '0'
        return figure
    
    def get_figures_from_board(self, id_game: int) -> List[FigureInBoard]:
        '''
            Función principal que obtiene las figuras de un tablero
        '''
        game = get_game(self.db, id_game)
        board = game.board_matrix
        figures = self.get_valid_figures(board)
        figures = self.normalize_figures(figures)
        for figure, indices in figures:
            figure_int = self.array_to_int(figure)
            figure_name = fig_values.get(int(figure_int), "Unknown")
            print(f"Figura: {figure_name}, Índices originales: {indices}")

        json_ws = {"event": "game.figures", "payload": {"type": figure_name, "indexes": indices}}