import pytest
from unittest.mock import MagicMock, Mock
from app.schemas.figure import FigureOut
from app.services.figures import FigureService
from app.utils.enums import FigureStatus, FigureType

class TestGetFigures:

    @pytest.mark.parametrize("player_id, game_started, player_figures, other_players_figures, expected_exception, expected_figures", [
        (123, True, 
         [Mock(id=1, type=FigureType.TYPE1, status=FigureStatus.INHAND),
          Mock(id=2, type=FigureType.TYPE2, status=FigureStatus.INDECK)],
         [Mock(id=3, type=FigureType.TYPE3, status=FigureStatus.INHAND)],
         None, 
         [FigureOut(id_figure=1, type_figure=FigureType.TYPE1, player_id=123),
          FigureOut(id_figure=3, type_figure=FigureType.TYPE3, player_id=456)]),
        (456, False, [], [], Exception("El juego no ha comenzado"), None),
        (789, True, [], [], None, []),
    ])
    def test_get_figures(self, mocker, player_id, game_started, player_figures, other_players_figures, expected_exception, expected_figures):
        # Mock get_player function
        mock_get_player = mocker.patch("app.services.figures.get_player")

        # Create mock game
        mock_game = Mock(started=game_started)

        # Create mock players
        mock_player = Mock(id=player_id, figures=player_figures, game=mock_game)
        mock_other_player = Mock(id=456, figures=other_players_figures)

        # Set up game players
        mock_game.players = [mock_player, mock_other_player]

        # Set return value for get_player
        mock_get_player.return_value = mock_player

        # Create FigureService instance
        instance = FigureService(db=MagicMock())

        if expected_exception:
            with pytest.raises(type(expected_exception)) as exc_info:
                instance.get_figures(player_id)
            assert str(exc_info.value) == str(expected_exception)
        else:
            figures = instance.get_figures(player_id)
            assert figures == expected_figures

        # Verify that get_player was called
        mock_get_player.assert_called_once_with(instance.db, player_id)