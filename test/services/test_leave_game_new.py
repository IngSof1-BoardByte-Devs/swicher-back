import pytest
from unittest.mock import MagicMock, patch
from app.services.game import GameService

@pytest.mark.asyncio
class TestGameService:
    @pytest.fixture
    def game_service(self):
        return GameService(db=MagicMock())

    @pytest.mark.parametrize("player_id, is_host, game_started, num_players, expected_return, should_delete_all", [
        (1, True, False, 4, {"status": "OK", "message": "Player left the game"}, True),
        (1, True, False, 1, {"status": "OK", "message": "Player left the game"}, True),
        (2, False, False, 4, {"status": "OK", "message": "Player left the game"}, False),
        (2, False, True, 4, {"status": "OK", "message": "Player left the game"}, False),
        (5, False, False, 0, Exception("Jugador no encontrado"), False),
    ])
    async def test_leave_game(self, game_service, player_id, is_host, game_started, num_players, expected_return, should_delete_all):
        with patch('app.services.game.get_player') as mock_get_player, \
             patch('app.services.game.get_game_by_player_id') as mock_get_game_by_player_id, \
             patch('app.services.game.delete_player') as mock_delete_player, \
             patch('app.services.game.manager.broadcast') as mock_broadcast, \
             patch('app.services.game.delete_all_game') as mock_delete_all_game:

            player = MagicMock(id=player_id, username=f"Player {player_id}")
            game = MagicMock(id=1, players=[MagicMock() for _ in range(num_players)], started=game_started)
            game.host = player if is_host else MagicMock(id=0)

            mock_get_player.return_value = player if player_id != 5 else None
            mock_get_game_by_player_id.return_value = game if player_id != 5 else None

            if isinstance(expected_return, Exception):
                with pytest.raises(Exception) as exc_info:
                    await game_service.leave_game(player_id)
                assert str(exc_info.value) == str(expected_return)
            else:
                result = await game_service.leave_game(player_id)
                assert result == expected_return

            mock_get_player.assert_called_once_with(game_service.db, player_id)
            if player_id != 5:
                mock_get_game_by_player_id.assert_called_once_with(game_service.db, player_id)
                mock_delete_player.assert_called()
                mock_broadcast.assert_called()
                if should_delete_all:
                    mock_delete_all_game.assert_called()
                else:
                    mock_delete_all_game.assert_not_called()