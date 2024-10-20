from unittest.mock import MagicMock
import pytest

from app.services.game import GameService
from app.database.crud import update_turn_game

"""Verifica solo los turnos, no controla las cartas"""

@pytest.mark.asyncio
class TestChangeTurn:
    def turn(self,id):
        turn = id
        if id >= 3 and id <= 5:
            turn = id - 2
        elif id >= 6 and id <= 9:
            turn = id - 5
        elif id >= 10:
            turn = 1
        return turn
    
    def mock_get_player(self,db, player_id):
        player = None
        if player_id in range(1,12):
            player = MagicMock(id = player_id, movements = [1,2,3])
            player.turn = self.turn(player_id) if player_id != 11 else 2
        return player
    
    def mock_get_game_by_player_id(self,db, player_id):
        game = None
        players = [[1,2],[3,4,5],[6,7,8,9],[10,20],[11,13]]
        for i in range(len(players)):
            if player_id in players[i]:
                game = MagicMock(id=i+1,players=players[i],started=(player_id!=10))
                game.turn = self.turn(player_id)     
        return game

    @pytest.mark.parametrize("player_id, expected_return", [
        #Todos los casos con dos jugadores
        (1, None),(2, None),
        #Todos los casos con tres jugadores
        (3, None),(4, None),(5, None),
        #Todos los casos con cuatro jugadores
        (6, None),(7, None),(8, None),(9, None),
        #Caso error jugador no encontrado
        (12, Exception("Jugador no encontrado")),
        #Caso error partida no iniciada
        (10, Exception("Partida no iniciada")),
        #Caso error no es turno del jugador
        (11, Exception("No es turno del jugador")), 
    ])
    async def test_change_turn(self, mocker, player_id, expected_return):
        #Mock cruds
        mock_get_player = mocker.patch("app.services.game.get_player")
        mock_get_game_by_player_id = mocker.patch("app.services.game.get_game_by_player_id")
        mock_manager_broadcast = mocker.patch("app.services.game.manager.broadcast")
        mock_parcial_movements_exist = mocker.patch("app.services.game.parcial_movements_exist")
        mock_get_figures_hand = mocker.patch("app.services.game.get_figures_hand")
        

        #Config cruds
        mock_get_player.side_effect = lambda db, player_id: self.mock_get_player(db,player_id)
        mock_get_game_by_player_id.side_effect = lambda db, player_id: self.mock_get_game_by_player_id(db,player_id)
        mock_parcial_movements_exist.return_value = False
        mock_get_figures_hand.return_value = [1,2,3]
        
        #Instancia db
        db = MagicMock()
        db.commit.return_value = None
        instance = GameService(db)
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                await instance.change_turn(player_id)

            #Verificaciones
            mock_manager_broadcast.assert_not_called()
        else:

            await instance.change_turn(player_id)

            #Verificaciones
            player = self.mock_get_player(db,player_id)
            game = self.mock_get_game_by_player_id(db,player_id)
            assert player.turn == game.turn
            update_turn_game(db,game)
            assert player.turn != game.turn
            assert game.turn == player.turn+1 or game.turn == 1

            mock_get_player.assert_called_once_with(instance.db, player_id)
            mock_get_game_by_player_id.assert_called_once_with(instance.db, player_id)
            assert mock_manager_broadcast.call_count == 1
            
            