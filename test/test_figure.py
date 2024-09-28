import pytest
from unittest.mock import MagicMock, Mock

from app.schemas.figure import FigureOut
from app.services.figures import FigureService

class TestGetFigures:

    @pytest.mark.parametrize("player_id, expected_exception, expected_figures", [
        (123, None, [FigureOut(card_id=1, figure_type="tipo1"), FigureOut(card_id=2, figure_type="tipo3")]),  
        (456, Exception("No existe jugador"), None),  
        (789, None, []),  
    ])
    def test_get_figures(self, mocker, player_id, expected_exception, expected_figures):
        # Simula la función `get_player`
        mock_get_player = mocker.patch("app.services.figures.get_player")

        # Mockea el objeto `player` con figuras (o sin figuras)
        mock_player = Mock()
        if player_id == 123:
            mock_player.figures.all.return_value = [
                Mock(id=1, type="tipo1", status="INHAND"),
                Mock(id=2, type="tipo3", status="INDECK"),
            ]
        elif player_id == 456:
            mock_player = None
        elif player_id == 789:
            mock_player.figures.all.return_value = []
            

        # Define el valor de retorno esperado
        mock_get_player.return_value = mock_player

        # Llama a la función `get_figures`
        instance = FigureService(db=MagicMock())

        if expected_exception:
            try:
                figuras = instance.get_figures(player_id)
            except Exception:
                pass  # Test pasa si se lanza la excepción esperada
            else:
                raise Exception("La excepción esperada no se lanzó")  # Test falla si no se lanza la excepción
        else:
            figuras = instance.get_figures(player_id)


        # Verificaciones
        if not expected_exception:
            # Verifica que `get_player` se llame con el ID correcto
            mock_get_player.assert_called_once_with(instance.db, player_id)

            # Verifica que se devuelvan los objetos `FigureOut` correctos (o una lista vacía)
            assert figuras == expected_figures