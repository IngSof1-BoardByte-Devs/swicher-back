import unittest
from unittest.mock import patch, MagicMock

import pytest

from app.schemas.game import JoinGame
from app.services.game import GameService

@pytest.mark.asyncio
class TestGameService:
    @patch('app.services.game.get_game')
    @patch('app.services.game.create_player')
    @patch('app.services.game.manager.broadcast')
    async def test_join_game_success(self,mock_broadcast,mock_create_player,mock_get_game):
        # Configuración del mock para un juego existente y con menos de 4 jugadores
        mock_game = MagicMock()
        mock_game.players = ["player1"]
        mock_game.started = False
        mock_game.id = 1
        mock_get_game.return_value = mock_game

        mock_player = MagicMock()
        mock_player.id = 1
        mock_player.username = "player1"
        mock_create_player.return_value = mock_player

        # Datos de entrada
        data = JoinGame(player_name="player2",game_id=1)


        # Instancia de la clase que contiene join_game
        instance = GameService(db=MagicMock())

        # Llamada al método
        response = await instance.join_game(data)


        # Verificaciones
        mock_create_player.assert_called_once_with(instance.db, "player2", mock_game)
        assert mock_broadcast.call_count == 2
        assert response.model_dump() == {"player_id": 1, "game_id": 1}



    @patch('app.services.game.get_game')
    @patch('app.services.game.create_player')
    @patch('app.services.game.manager.broadcast')
    async def test_join_border_game_success(self,mock_broadcast,mock_create_player,mock_get_game):
        mock_game = MagicMock()
        mock_game.players = ["player1", "player2", "player3"]
        mock_game.started = False
        mock_game.id = 1
        mock_get_game.return_value = mock_game

        mock_player = MagicMock()
        mock_player.id = 4
        mock_player.username = "player4"
        mock_create_player.return_value = mock_player
        
        data = JoinGame(player_name="player4",game_id=4)

        instance = GameService(db=MagicMock())
        response = await instance.join_game(data)

        mock_create_player.assert_called_once_with(instance.db, "player4", mock_game)
        assert mock_broadcast.call_count == 2
        assert response.model_dump() == {"player_id": 4, "game_id": 1}


    @patch('app.services.game.get_game')
    async def test_join_game_non_existent_game(self,mock_get_game):
        # Configuración del mock para un juego que no existe
        mock_get_game.return_value = None

        data = JoinGame(player_name="player1",game_id=1)
        instance = GameService(db=MagicMock())

        # Verificar que se lanza la excepción
        with pytest.raises(Exception) as context:
            await instance.join_game(data)

        assert str(context.value) == "Partida no encontrada"


    @patch('app.services.game.get_game')
    async def test_join_game_max_players_exceeded(self, mock_get_game):
        # Configuración del mock para un juego con 4 jugadores
        mock_game = MagicMock()
        mock_game.players = ["player1", "player2", "player3", "player4"]
        mock_game.started = False
        mock_get_game.return_value = mock_game

        data = JoinGame(player_name="player5",game_id=1)
        instance = GameService(db=MagicMock())

        # Verificar que se lanza la excepción
        with pytest.raises(Exception) as context:
            await instance.join_game(data)

        assert str(context.value) == "Partida con máximo de jugadores permitidos"

    async def test_join_game_not_name(self):
        # Configuración del mock para un juego con 4 jugadores

        data = JoinGame(player_name="",game_id=1)
        instance = GameService(db=MagicMock())

        # Verificar que se lanza la excepción
        with pytest.raises(Exception) as context:
            await instance.join_game(data)

        assert str(context.value) == "El jugador debe tener un nombre"

    @patch('app.services.game.get_game')
    async def test_join_game_started_game(self, mock_get_game):
        # Configuración del mock para un juego con 4 jugadores
        mock_game = MagicMock()
        mock_game.players = ["player1", "player2", "player3"]
        mock_game.started = True
        mock_get_game.return_value = mock_game

        data = JoinGame(player_name="player4",game_id=1)
        instance = GameService(db=MagicMock())

        # Verificar que se lanza la excepción
        with pytest.raises(Exception) as context:
            await instance.join_game(data)

        assert str(context.value) == "Partida ya iniciada"