import pytest
from unittest.mock import MagicMock, Mock
from app.schemas.figure import FigUpdate
from app.services.figures import FigureService
from app.utils.enums import FigureStatus, FigureType

class TestUpdateFigureServiceStatus:

    @pytest.mark.parametrize("figure_id, player_id, game_started, turn, figure_exists, figure_player_id, figure_status, expected_exception, expected_response", [
        (1, 100, True, 100, True, 100, FigureStatus.INHAND, None, 
         FigUpdate(id=1, id_player=100, type=FigureType.TYPE1, discarded=False, blocked=False)),
        (2, 101, True, 101, False, None, FigureStatus.DISCARDED, Exception("La carta de figura no existe"), None),
        (3, 102, False, 102, True, 102, FigureStatus.DISCARDED, Exception("La partida no ha comenzado"), None),
        (4, 103, True, 104, True, 103, FigureStatus.BLOCKED, Exception("No es tu turno"), None),
        (5, 105, True, 105, True, 106, FigureStatus.INHAND, Exception("La carta no te pertenece"), None),
    ])
    def test_update_figure_service_status(self, mocker, figure_id, player_id, game_started, turn, figure_exists, figure_player_id, figure_status, expected_exception, expected_response):
        # Mock get_figure_by_id function
        mock_get_figure_by_id = mocker.patch("app.services.figures.get_figure_by_id")
        
        if figure_exists:
            # Create mock figure and game
            mock_figure = Mock(id=figure_id, type=FigureType.TYPE1, status=figure_status, player=Mock(id=figure_player_id), game=Mock(started=game_started, turn=turn))
            mock_get_figure_by_id.return_value = mock_figure
        else:
            mock_get_figure_by_id.return_value = None
        
        # Mock update_figure_status function
        mock_update_figure_status = mocker.patch("app.services.figures.update_figure_status")
        
        if figure_exists:
            mock_update_figure_status.return_value = mock_figure

        # Mock delete_partial_movements and remove_player_from_figure functions
        mock_delete_partial_movements = mocker.patch("app.services.figures.delete_partial_movements")
        mock_remove_player_from_figure = mocker.patch("app.services.figures.remove_player_from_figure")

        # Create FigureService instance
        instance = FigureService(db=MagicMock())

        # Mock prepare_figure_update_response method
        instance.prepare_figure_update_response = Mock(return_value=expected_response)

        if isinstance(expected_exception, Exception):
            with pytest.raises(Exception, match=str(expected_exception)) as exc_info:
                instance.update_figure_service_status(figure_id, player_id)
        else:
            response = instance.update_figure_service_status(figure_id, player_id)
            assert response == expected_response

        # Verify that get_figure_by_id was called
        mock_get_figure_by_id.assert_called_once_with(instance.db, figure_id)

        if figure_exists and game_started and turn == player_id and figure_player_id == player_id:
            # Verify that update_figure_status was called with the correct parameters
            mock_update_figure_status.assert_called_once_with(instance.db, mock_figure)

            if figure_status == FigureStatus.DISCARDED:
                # Verify that delete_partial_movements and remove_player_from_figure were called
                mock_delete_partial_movements.assert_called_once_with(instance.db, mock_figure.game)
                mock_remove_player_from_figure.assert_called_once_with(instance.db, mock_figure)

            # Verify that prepare_figure_update_response was called with the correct parameters
            instance.prepare_figure_update_response.assert_called_once_with(mock_update_figure_status.return_value, figure_player_id)
