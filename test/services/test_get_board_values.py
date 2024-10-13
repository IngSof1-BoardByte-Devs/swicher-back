from unittest.mock import MagicMock
import pytest

from app.schemas.board import BoardOut, Color
from app.services.board import BoardService


class TestBoardValues:
    def mock_get_game(self,game_id,mock_games):
        return next((g for g in mock_games if g.id == game_id), None)
    
    @pytest.mark.parametrize("game_id, expected_return", [
        #Caso normal
        (1,BoardOut(board= [Color(color=1)]*36)),
        #Caso con error partida no encontrada
        (3, Exception("Partida no encontrada")),
        #Caso con error partida no iniciada
        (2, Exception("Partida no iniciada")),
    ])
    def test_get_board_values(self, mocker, game_id, expected_return):

        #Mock cruds
        mock_get_game = mocker.patch("app.services.board.get_game")

        #Mock elementos de base de datos
        mock_games = [MagicMock(id=1,started=True),
                      MagicMock(id=2,started=False,board_matrix=None)]
        mock_games[0].board_matrix = [1]*36

        #Config cruds
        mock_get_game.side_effect = lambda db, game_id: self.mock_get_game(game_id,mock_games)

        #Instancia db
        db=MagicMock()
        db.commit.return_value = None
        instance = BoardService(db)
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                instance.get_board_values(game_id)
        else:
            result = instance.get_board_values(game_id)
            assert result == expected_return

        #Verificaciones
        mock_get_game.assert_called_once_with(instance.db, game_id)