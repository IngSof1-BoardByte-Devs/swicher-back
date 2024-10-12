import pytest
from unittest.mock import MagicMock, Mock
from app.schemas.figure import FigureOut
from app.services.figures import FigureService
from app.utils.enums import FigureStatus, FigureType

class TestGetFigures:

    @pytest.mark.parametrize("game_id, game_exists, players_figures, expected_exception, expected_figures", [
        (123, True, [
            [Mock(id=1, type=FigureType.TYPE1, status=FigureStatus.INHAND),
             Mock(id=2, type=FigureType.TYPE2, status=FigureStatus.INDECK)],
            [Mock(id=3, type=FigureType.TYPE3, status=FigureStatus.INHAND)]
        ], None, [
            FigureOut(player_id=1, id_figure=1, type_figure=FigureType.TYPE1),
            FigureOut(player_id=2, id_figure=3, type_figure=FigureType.TYPE3)
        ]),
        (456, False, [], Exception("Partida no encontrada"), None),
        (789, True, [[], []], None, []),
    ])
    def test_get_figures(self, mocker, game_id, game_exists, players_figures, expected_exception, expected_figures):
        # Mock get_game function
        mock_get_game = mocker.patch("app.services.figures.get_game")

        if game_exists:
            # Create mock game and players
            mock_game = Mock()
            mock_players = []
            for i, figures in enumerate(players_figures):
                mock_player = Mock(id=i+1, figures=figures)
                mock_players.append(mock_player)
            mock_game.players = mock_players
            mock_get_game.return_value = mock_game
        else:
            mock_get_game.return_value = None

        # Create FigureService instance
        instance = FigureService(db=MagicMock())

        if isinstance(expected_exception, Exception):
            with pytest.raises(Exception, match=str(expected_exception)) as exc_info:
                instance.get_figures(game_id)
        else:
            figures = instance.get_figures(game_id)
            assert figures == expected_figures

        # Verify that get_game was called
        mock_get_game.assert_called_once_with(instance.db, game_id)