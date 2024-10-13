from unittest.mock import MagicMock
import pytest

from app.services.game import GameService

@pytest.mark.asyncio
class TestLeaveGame:
    def mock_get_player(self, player_id):
        player = None
        if player_id == 2 or player_id == 3:
            player = MagicMock(id = player_id, username = f"Player {player_id}")
            player.return_value = player_id
        return player
    
    def mock_get_game_by_player_id(self, player_id, player):
        game = None
        if player_id == 3:
            game = MagicMock(id=1,players=[1,2,player])
        elif player_id == 2:
            game = MagicMock(id=1,players=[1,player])
        return game


    def delete_player(self, db, player, game):
        game.players.remove(player)


    @pytest.mark.parametrize("player_id, expected_return", [
        #Caso que queden mas de dos jugadores
        (3,{"status": "OK", "message": "Player left the game"}),
        #Caso que quede un solo jugador
        (2,{"status": "OK", "message": "Player left the game"}),
        #Caso que no encuentra al jugador
        (5,Exception("Jugador no encontrado")),
    ])
    async def test_leave_game(self, mocker, player_id, expected_return):

        #Mock cruds
        mock_get_player = mocker.patch("app.services.game.get_player")
        mock_get_game_by_player_id = mocker.patch("app.services.game.get_game_by_player_id")
        mock_delete_player = mocker.patch("app.services.game.delete_player")
        mock_manager_broadcast = mocker.patch("app.services.game.manager.broadcast")
        mock_delete_all_game = mocker.patch("app.services.game.delete_all_game")

        #Config cruds
        mock_get_player.return_value = self.mock_get_player(player_id)
        mock_get_game_by_player_id.side_effect = lambda db, player_id: self.mock_get_game_by_player_id(
            player_id,mock_get_player.return_value)
        mock_delete_player.side_effect = lambda db, player, game: self.delete_player(db, player, game)

        mock_manager_broadcast.return_value = None
        mock_delete_all_game.return_value = None

        #Instancia db
        instance = GameService(db=MagicMock())
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                await instance.leave_game(player_id)
        else:
            result = await instance.leave_game(player_id)
            assert result == expected_return

        #Verificaciones
        mock_get_player.assert_called_once_with(instance.db, player_id)
        if isinstance(expected_return, Exception):
            mock_get_game_by_player_id.assert_not_called()
            mock_delete_player.assert_not_called()
            mock_manager_broadcast.assert_not_called()
            mock_delete_all_game.assert_not_called()
        else:
            mock_get_game_by_player_id.assert_called_once_with(instance.db, player_id)
            mock_delete_player.assert_called()
            mock_manager_broadcast.assert_called()
            if(player_id==2):
                mock_delete_all_game.assert_called()
            else:
                mock_delete_all_game.assert_not_called()