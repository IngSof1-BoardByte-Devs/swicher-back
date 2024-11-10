from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import SingleGameOut
from app.schemas.player import PlayerOut


class TestGetMovements:

    @pytest.mark.parametrize("game_id, expected_exception", [
        (1, None),
        (2, HTTPException(status_code=404, detail="Partida no encontrada")),
        (1, HTTPException(status_code=500, detail="Internal server error")),
    ])
    def test_get_game(self, mocker, game_id, expected_exception):
        # Cliente
        client = TestClient(app)

        # Respuesta de base de datos
        game = [SingleGameOut(id=1, name="test", started=False, turn=0, 
                              bloqued_color=None, players=[PlayerOut(id=1, username="player", turn=0)], timer=0)]
        
        # Simula la función de get_game
        mock_get_game = mocker.patch("app.services.game.GameService.get_game")

        # Simulo la respuesta de get_game
        if game_id == game[0].id:
            if not expected_exception:
                mock_get_game.return_value = game[0]
            else:
                mock_get_game.side_effect = Exception("Internal server error")
        else:
            mock_get_game.side_effect = Exception("Partida no encontrada")
        
        # Verifico si get_game devuelve error o no
        response = client.get(f"/games/{game_id}")
        if expected_exception:
            assert response.status_code == expected_exception.status_code
            assert response.json() == {"detail": expected_exception.detail}  
        else:
            assert response.status_code == 200
            assert response.json() == {"id": 1, "name": "test", "started": False,
                                       "turn": 0, "bloqued_color": None, 
                                       "players": [{"id": 1, "username": "player", "turn": 0}], "timer": 0}