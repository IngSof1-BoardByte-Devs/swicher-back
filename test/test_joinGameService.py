""" import unittest
from unittest.mock import patch, MagicMock

from app.schemas.game import JoinGame
from app.services.game import GameService

class TestGameService(unittest.TestCase):
    @patch('app.services.game.get_game')
    @patch('app.services.game.create_player')
    def test_join_game_success(self,mock_create_player,mock_get_game):
        # Configuración del mock para un juego existente y con menos de 4 jugadores
        mock_game = MagicMock()
        mock_game.players.all.return_value = ["player1"]
        mock_game.started = False
        mock_get_game.return_value = mock_game

        # Datos de entrada
        data = JoinGame(player_name="player2",game_id=1)

        # Instancia de la clase que contiene join_game
        instance = GameService(db=MagicMock())

        # Llamada al método
        instance.join_game(data)


        # Verificar que se llama a create_player
        mock_create_player.assert_called_once_with(instance.db, "player2", mock_game)


    @patch('app.services.game.get_game')
    @patch('app.services.game.create_player')
    def test_join_border_game_success(self,mock_create_player, mock_get_game):
        mock_game = MagicMock()
        mock_game.players.all.return_value = ["player1", "player2", "player3"]
        mock_game.started = False
        mock_get_game.return_value = mock_game
        
        data = JoinGame(player_name="player4",game_id=1)
        instance = GameService(db=MagicMock())
        instance.join_game(data)

        mock_create_player.assert_called_once_with(instance.db, "player4", mock_game)


    @patch('app.services.game.get_game')
    def test_join_game_non_existent_game(self,mock_get_game):
        # Configuración del mock para un juego que no existe
        mock_get_game.return_value = None

        data = JoinGame(player_name="player1",game_id=1)
        instance = GameService(db=MagicMock())

        # Verificar que se lanza la excepción
        with self.assertRaises(Exception) as context:
            instance.join_game(data)

        self.assertEqual(str(context.exception), "Error: User tries to join a non-existent game")


    @patch('app.services.game.get_game')
    def test_join_game_max_players_exceeded(self, mock_get_game):
        # Configuración del mock para un juego con 4 jugadores
        mock_game = MagicMock()
        mock_game.players.all.return_value = ["player1", "player2", "player3", "player4"]
        mock_game.started = False
        mock_get_game.return_value = mock_game

        data = JoinGame(player_name="player5",game_id=1)
        instance = GameService(db=MagicMock())

        # Verificar que se lanza la excepción
        with self.assertRaises(Exception) as context:
            instance.join_game(data)

        self.assertEqual(str(context.exception), "Error: Maximum players allowed")

if __name__ == '__main__':
    unittest.main() """