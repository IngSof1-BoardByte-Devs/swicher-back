from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import CreateGame, PlayerAndGame


class TestCreateGame:

    @pytest.mark.parametrize("game_data, expected_exception", [
        # Caso normal
        (CreateGame(player_name="player", game_name="game", password="password"), None),
        # Caso sin nombre del jugador
        (CreateGame(player_name="", game_name="game", password="password"),
            HTTPException(status_code=400, detail="El jugador debe tener un nombre")),
        # Caso sin nombre de la partida
        (CreateGame(player_name="player", game_name="", password="password"),
            HTTPException(status_code=400, detail="La partida debe tener un nombre")),
        # Caso excepcional
        (CreateGame(player_name="player", game_name="game", password="password"),
            HTTPException(status_code=500, detail="Internal server error"))
    ])
    def test_create_game(self, mocker, game_data, expected_exception):
        # Cliente
        client = TestClient(app)

        # Respuesta de base de datos
        game = PlayerAndGame(player_id=1, game_id=1)
        
        # Simula la función de create_game
        mock_create_game = mocker.patch("app.services.game.GameService.create_game")

        # Simulo la respuesta de create_game
        if game_data.player_name:
            if game_data.game_name:
                if not expected_exception:
                    mock_create_game.return_value = game
                else:
                    mock_create_game.side_effect = Exception("Internal server error")
            else:
                mock_create_game.side_effect = Exception("La partida debe tener un nombre")
        else:
            mock_create_game.side_effect = Exception("El jugador debe tener un nombre")
        
        # Verifico si create_game devuelve error o no
        response = client.post("/games/", json=game_data.model_dump())
        if expected_exception:
            assert response.status_code == expected_exception.status_code
            assert response.json() == {"detail": expected_exception.detail}  
        else:
            assert response.status_code == 200
            assert response.json() == {"player_id": 1, "game_id": 1}