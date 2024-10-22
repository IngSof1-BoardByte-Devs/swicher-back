from unittest.mock import MagicMock
import pytest

from app.services.game import GameService

@pytest.mark.asyncio
class TestStartGame:
    def mock_get_player(self,db, player_id):
        player = None
        if player_id in [1,2,3,5,6,7]:
            player = MagicMock(id = player_id)
        return player
    
    def mock_get_game_by_player_id(self,db, player_id):
        game = None
        players = [[1,2,3],[5,6],[7]]
        for i in range(len(players)):
            if player_id in players[i]:
                game = MagicMock(id=i+1,players=players[i],started=(i+1==2))
                game.host = self.mock_get_player(db, players[i][0])
        return game


    @pytest.mark.parametrize("player_id, expected_return", [
        #Caso normal
        (1, {"status": "OK", "message": "Game started"}),
        #Caso error jugador no encontrado
        (4, Exception("Jugador no encontrado")),
        #Caso error partida ya iniciada
        (5, Exception("La partida ya se inició")),
        #Caso error de iniciarla alguien que no es el dueño
        (2, Exception("Sólo el dueño puede iniciar la partida")),
        #Caso error de iniciarla con menos de 2 jugadores
        (7, Exception("La partida debe tener entre 2 a 4 jugadores para iniciar")),      
    ])
    async def test_start_game(self, mocker, player_id, expected_return):
        #Mock cruds
        mock_get_player = mocker.patch("app.services.game.get_player")
        mock_get_game_by_player_id = mocker.patch("app.services.game.get_game_by_player_id")
        mock_put_start_game = mocker.patch("app.services.game.put_start_game")
        mock_put_asign_turn = mocker.patch("app.services.game.put_asign_turn")
        mock_create_movement_deck = mocker.patch("app.services.game.MoveService.create_movement_deck")
        mock_create_figure_deck = mocker.patch("app.services.game.FigureService.create_figure_deck")
        mock_create_board = mocker.patch("app.services.game.BoardService.create_board")
        mock_manager_broadcast = mocker.patch("app.services.game.manager.broadcast")
        

        #Config cruds
        mock_get_player.side_effect = lambda db, player_id: self.mock_get_player(db,player_id)
        mock_get_game_by_player_id.side_effect = lambda db, player_id: self.mock_get_game_by_player_id(db,player_id)
        
        #Instancia db
        instance = GameService(db=MagicMock())
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                await instance.start_game(player_id)
        else:
            result = await instance.start_game(player_id)
            assert result == expected_return

        #Verificaciones
        if isinstance(expected_return, Exception):
            mock_put_start_game.assert_not_called()
            mock_put_asign_turn.assert_not_called()
            mock_create_movement_deck.assert_not_called()
            mock_create_figure_deck.assert_not_called()
            mock_create_board.assert_not_called()
            mock_manager_broadcast.assert_not_called()
        else:
            mock_get_player.assert_called_once_with(instance.db, player_id)
            mock_get_game_by_player_id.assert_called_once_with(instance.db, player_id)
            assert mock_put_start_game.call_count == 1
            assert mock_put_asign_turn.call_count == len(
                self.mock_get_game_by_player_id(instance.db,player_id).players)
            assert mock_create_movement_deck.call_count == 1
            assert mock_create_figure_deck.call_count == 1
            assert mock_create_board.call_count == 1
            assert mock_manager_broadcast.call_count == 2
            