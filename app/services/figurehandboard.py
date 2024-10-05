from app.schemas.board import *
from app.schemas.figure import *
from app.services.board import *
from app.services.figures import *
from sqlalchemy.orm import Session

class FigureHandBoard:
    def __init__(self, db: Session, game_id: int, player_id: int):
        self.db = db
        self.game_id = game_id
        self.player_id = player_id
        self.board_service = BoardService(db)
        self.figure_service = FigureService(db)

    def get_figures_in_hand(self):
        figures = self.figure_service.get_figures(self.game_id)
        player_figures = [fig for fig in figures if fig.player_id == self.player_id]
        return player_figures

    def get_board_state(self):
        board = self.board_service.get_board_values(self.game_id)
        return board

    def confirm_figure(self, figure_id: int):
        figure = self.figure_service.get_figure(figure_id)
        if figure.player_id == self.player_id and figure.status == FigureStatus.INHAND:
            return True
        return False

    def play_figure(self, figure_id: int, position: Position):
        # Lógica para jugar una figura en una posición específica
        pass


