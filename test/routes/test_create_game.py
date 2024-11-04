from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import CreateGame, PlayerAndGame


class TestGetMovements:

    @pytest.mark.parametrize("game_data, expected_return, expected_status, expected_service", [
        #Caso normal
        (CreateGame(player_name="player",game_name="game"),
         {"msg": "La partida se creó con éxito",
	     "game_id": 1,
	     "player_id": 1},
         200, PlayerAndGame(game_id=1,player_id=1)),
        #Caso sin nombre del jugador 
        (CreateGame(player_name="",game_name="game"),
         {"detail": "Nombre de jugador incorrecto"},
         400, Exception("Nombre de jugador incorrecto")),
        #Caso sin nombre de la partida 
        (CreateGame(player_name="player",game_name=""),
         {"detail": "Nombre de partida incorrecto"},
         400, Exception("Nombre de partida incorrecto")),
        #Caso excepcional
        (CreateGame(player_name="player",game_name="game"),
         {"detail": "Internal server error"},
         500, Exception("Internal server error")),
    ])
    def test_get_game(self, mocker, game_data, expected_return, expected_status, expected_service):
        #Cliente
        client = TestClient(app)
        
        #Simula la función de create_game
        mock_create_game = mocker.patch("app.routes.game.GameService.create_game")

        if isinstance(expected_service, Exception):
            mock_create_game.side_effect = expected_service
        else:
            mock_create_game.return_value = expected_service
        
        #Instancio la función
        response = client.post("/games/", json=game_data.model_dump())
        assert response.status_code == expected_status
        assert response.json() == expected_return
