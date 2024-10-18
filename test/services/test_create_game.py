from unittest.mock import MagicMock
import pytest

from app.schemas.game import CreateGame, PlayerAndGame
from app.services.game import GameService

@pytest.mark.asyncio
class TestCreateGame:
    def mock_create_player(self, db, player_name, game):
        new_player = MagicMock(id=1)
        new_player.name = player_name
        game.players.append(new_player)
        return new_player
    
    def mock_create_game(self, db, game_name):
        new_game = MagicMock(id=1,players=[])
        new_game.name = game_name
        return new_game

    @pytest.mark.parametrize("game_data, expected_return", [
        #Caso normal
        (CreateGame(player_name="player",game_name="game"),
         PlayerAndGame(player_id=1,game_id=1)),
        #Caso error falta nombre de jugador
        (CreateGame(player_name="",game_name="game"),
         Exception("El jugador debe tener un nombre")),
        #Caso error falta nombre de partida
        (CreateGame(player_name="player",game_name=""),
         Exception("La partida debe tener un nombre")),

    ])
    async def test_create_game(self, mocker, game_data, expected_return):
        #Mock cruds
        mock_create_game = mocker.patch("app.services.game.create_game")
        mock_create_player = mocker.patch("app.services.game.create_player")
        mock_manager_broadcast = mocker.patch("app.services.game.manager.broadcast")

        #Config cruds
        mock_create_player.side_effect = lambda db, player_name, game: self.mock_create_player(db,player_name, game)
        mock_create_game.side_effect = lambda db, game_name: self.mock_create_game(db,game_name)
        
        #Instancia db
        db = MagicMock()
        db.commit.return_value = None
        instance = GameService(db)
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                await instance.create_game(game_data)
        else:
            result = await instance.create_game(game_data)
            assert result == expected_return

        #Verificaciones
        if isinstance(expected_return, Exception):
            mock_create_game.assert_not_called()
            mock_create_player.assert_not_called()
            mock_manager_broadcast.assert_not_called()
        else:
            mock_create_game.assert_called_once_with(instance.db, game_data.game_name)
            mock_create_player.assert_called()
            mock_manager_broadcast.assert_called()