from unittest.mock import MagicMock
import pytest

from app.schemas.game import SingleGameOut
from app.schemas.player import PlayerOut
from app.services.game import GameService
from app.database.models import Game, Player
from datetime import datetime, timezone


class TestGetGame:
    def mock_get_game(self, game_id):
        if game_id == 1:
            # Devuelve una instancia que imite el modelo de base de datos Game
            return Game(
                id=1,
                name="Partida no empezada",
                started=False,
                turn=0,
                bloqued_color=None,
                time_last_turn=datetime(2024, 1, 1, tzinfo=timezone.utc),  # Valor de ejemplo
                players=[
                    Player(id=1, username="Player 1", turn=1),
                    Player(id=2, username="Player 2", turn=2)
                ]
            )
        elif game_id == 2:
            return Game(
                id=2,
                name="Partida empezada",
                started=True,
                turn=2,
                bloqued_color=2,
                time_last_turn=datetime(2024, 1, 1, tzinfo=timezone.utc),  # Valor de ejemplo
                players=[
                    Player(id=1, username="Player 1", turn=1),
                    Player(id=2, username="Player 2", turn=2),
                    Player(id=3, username="Player 3", turn=3),
                    Player(id=4, username="Player 4", turn=4)
                ]
            )
        else:
            return None

    @pytest.mark.parametrize("game_id, expected_return", [
        (1, SingleGameOut(
            id=1,
            name="Partida no empezada",
            started=False,
            turn=0,
            bloqued_color=None,
            timer=0,
            players=[
                PlayerOut(id=1, username="Player 1", turn=1),
                PlayerOut(id=2, username="Player 2", turn=2)
            ]
        )),
        (2, SingleGameOut(
            id=2,
            name="Partida empezada",
            started=True,
            turn=2,
            bloqued_color=2,
            timer=0,
            players=[
                PlayerOut(id=1, username="Player 1", turn=1),
                PlayerOut(id=2, username="Player 2", turn=2),
                PlayerOut(id=3, username="Player 3", turn=3),
                PlayerOut(id=4, username="Player 4", turn=4)
            ]
        )),
        (3, Exception("Partida no encontrada"))
    ])
    def test_get_game(self, mocker, game_id, expected_return):

        # Mock cruds
        mock_get_game = mocker.patch("app.services.game.get_game")

        # Config cruds
        mock_get_game.return_value = self.mock_get_game(game_id)

        # Instancia db
        instance = GameService(db=MagicMock())
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                instance.get_game(game_id)
        else:
            result = instance.get_game(game_id)
            print(result)
            print(expected_return)
            # Excluir el atributo 'timer' de la comparación
            # Excluir el atributo 'timer' de la comparación
            assert {k: v for k, v in result.model_dump().items() if k != 'timer'} == {k: v for k, v in expected_return.model_dump().items() if k != 'timer'}



        # Verificaciones
        mock_get_game.assert_called_once_with(instance.db, game_id)
