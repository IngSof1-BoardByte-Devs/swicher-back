import pytest
from unittest.mock import MagicMock, Mock

from app.schemas.movement import MovementOut
from app.services.movement import MoveService

class TestGetMovements:

    @pytest.mark.parametrize("player_id, game_started, expected_exception, expected_movements", [
        (123, True, None, [MovementOut(card_id=1, movement_type="tipo1"), MovementOut(card_id=2, movement_type="tipo3")]),  # Jugador con cartas
        (456, True, Exception("No existe jugador"), None),  # Jugador no existe
        (789, True, None, []),  # Jugador sin cartas
        (101, False, Exception("La partida no está empezada"), None),  # Partida no empezada
    ])
    def test_get_movements(self, mocker, player_id, game_started, expected_exception, expected_movements):
        # Simula la función `get_player`
        mock_get_player = mocker.patch("app.services.movement.get_player")

        # Simula la función `get_game_by_player_id`
        mock_get_game = mocker.patch("app.services.movement.get_game_by_player_id")

        # Mockea el objeto `player` con movimientos (o sin movimientos)
        mock_player = Mock()
        if player_id == 123:
            mock_player.movements = [
                Mock(id=1, type="tipo1"),
                Mock(id=2, type="tipo3"),
            ]
        elif player_id == 456:
            mock_player = None
        elif player_id == 789 or player_id == 101:
            mock_player.movements = []

        # Mockea el objeto `game`
        mock_game = Mock()
        mock_game.started = game_started

        # Define los valores de retorno esperados
        mock_get_player.return_value = mock_player
        mock_get_game.return_value = mock_game

        # Crea una instancia de MoveService
        instance = MoveService(db=MagicMock())
        if expected_exception:
            with pytest.raises(type(expected_exception), match=str(expected_exception)):
                instance.get_movements(player_id)
        else:
            movimientos = instance.get_movements(player_id)
            assert movimientos == expected_movements

        # Verificaciones
        mock_get_player.assert_called_once_with(instance.db, player_id)
        if mock_player:
            mock_get_game.assert_called_once_with(instance.db, player_id)
            