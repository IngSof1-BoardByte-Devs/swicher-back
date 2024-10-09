from unittest.mock import MagicMock
import pytest

from app.schemas.game import SingleGameOut
from app.schemas.player import PlayerOut
from app.services.game import GameService


class TestGetGame:
    def mock_get_game(self, game_id):
        game = None
        if game_id == 1:
            game = MagicMock(id=game_id, started=False, turn=0, bloqued_color=None)
            game.name = "Partida no empezada"
            players = []
            players.extend(MagicMock(username=f"Player {i}", id=i, turn=i) for i in range(1,3))
            game.players = players
        elif game_id == 2:
            game = MagicMock(id=game_id, started=True, turn=2, bloqued_color=2)
            game.name = "Partida empezada"
            players = []
            players.extend(MagicMock(username=f"Player {i}", id=i, turn=i) for i in range(1,5))
            game.players = players
        return game

    
    def expected(game_id):
        result = None
        if game_id == 1:
            result = SingleGameOut(id=game_id,name="Partida no empezada", started=False,
                                   turn=0, bloqued_color=None,
                                   players=[PlayerOut(id=1 ,username="Player 1", turn=1),
                                            PlayerOut(id=2 ,username="Player 2", turn=2)])
        elif game_id == 2:
            result = SingleGameOut(id=game_id,name="Partida empezada", started=True,
                                   turn=2, bloqued_color=2,
                                   players=[PlayerOut(id=1 ,username="Player 1", turn=1),
                                            PlayerOut(id=2 ,username="Player 2", turn=2),
                                            PlayerOut(id=3 ,username="Player 3", turn=3),
                                            PlayerOut(id=4 ,username="Player 4", turn=4)])
        return result

    

    @pytest.mark.parametrize("game_id, expected_return", [
        #Caso partida no empezada
        (1,expected(1)),
        #Caso partida empezada
        (2,expected(2)),
        #Caso que no encuentra la partida
        (3,Exception("Partida no encontrada"))
    ])
    def test_get_game(self, mocker, game_id, expected_return):

        #Mock cruds
        mock_get_game = mocker.patch("app.services.game.get_game")

        #Config cruds
        mock_get_game.return_value = self.mock_get_game(game_id)

        #Instancia db
        instance = GameService(db=MagicMock())
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                instance.get_game(game_id)
        else:
            result = instance.get_game(game_id)
            assert result == expected_return

        #Verificaciones
        mock_get_game.assert_called_once_with(instance.db, game_id)