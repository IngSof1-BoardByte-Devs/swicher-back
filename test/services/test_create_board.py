from unittest.mock import MagicMock
import pytest

from app.database.crud import update_board
from app.services.board import BoardService


class TestCreateBoard:
    def mock_get_game(self,id_game,games):
        game = None
        for g in games:
            if id_game == g.id:
                game = g
                break
        return game

    @pytest.mark.parametrize("id_game", [1])
    def test_(self, mocker, id_game):

        #Mock cruds
        mock_get_game = mocker.patch("app.services.board.get_game")

        #Mock global
        game = MagicMock()
        game.id = id_game
        game.board_matrix = None
        games = [game]


        #Config cruds
        mock_get_game.side_effect = lambda db, id_game: self.mock_get_game(id_game,games)

        #Instancia db
        db=MagicMock()
        db.commit.return_value = None
        instance = BoardService(db)

        #Verificación previa
        assert not self.mock_get_game(id_game,games).board_matrix

        instance.create_board(id_game)

        #Verificaciones
        assert self.mock_get_game(id_game,games).matrix
        mock_get_game.assert_called_once_with(instance.db, id_game)
        