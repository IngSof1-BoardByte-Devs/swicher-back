""" import pytest
from unittest.mock import MagicMock, Mock

from app.schemas.movement import MovementOut
from app.services.movement import MoveService

class TestGetMovements:

    @pytest.mark.parametrize("player_id, expected_exception, expected_movements", [
        (123, None, [MovementOut(card_id=1, movement_type="tipo1"), MovementOut(card_id=2, movement_type="tipo3")]),  # Jugador con cartas
        (456, Exception("No existe jugador"), None),  # Jugador no existe
        (789, None, []),  # Jugador sin cartas
    ])
    def test_get_movements(self, mocker, player_id, expected_exception, expected_movements):
        # Simula la función `get_player`
        mock_get_player = mocker.patch("app.services.movement.get_player")

        # Mockea el objeto `player` con movimientos (o sin movimientos)
        mock_player = Mock()
        if player_id == 123:
            mock_player.movement.all.return_value = [
                Mock(id=1, type="tipo1"),
                Mock(id=2, type="tipo3"),
            ]
        elif player_id == 456:
            mock_player = None
        elif player_id == 789:
            mock_player.movement.all.return_value = []
            

        # Define el valor de retorno esperado
        mock_get_player.return_value = mock_player

        # Llama a la función `get_movements`
        instance = MoveService(db = MagicMock())

        instance = MoveService(db = MagicMock())
        if expected_exception:
            try:
                movimientos = instance.get_movements(player_id)
            except Exception:
                pass  # Test pasa si se lanza la excepción esperada
            else:
                raise Exception("La excepción esperada no se lanzó")  # Test falla si no se lanza la excepción
        else:
            movimientos = instance.get_movements(player_id)


        # Verificaciones
        if not expected_exception:
            # Verifica que `get_player` se llame con el ID correcto
            mock_get_player.assert_called_once_with(instance.db, player_id)

            # Verifica que se devuelvan los objetos `MovementOut` correctos (o una lista vacía)
            assert movimientos == expected_movements """