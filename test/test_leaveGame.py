from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.schemas.game import GameTest, PlayerTest, LeaveStartGame
from fastapi.encoders import jsonable_encoder

client = TestClient(app)


def test_leave_game():
    # Crear un juego con un jugador(host)
    mock_game = GameTest(id=1, name="test_game", players=["test_player"])
    # Crear un jugador
    mock_player1 = PlayerTest(id=1, username="test_player", game=1, host_game=1)
    leave_game_request = LeaveStartGame(player_id=1, game_id=1)

    with patch('app.services.game.GameService.leave_game', return_value=None):
        response = client.post("/game/leave_game", json=jsonable_encoder(leave_game_request))
        assert response.status_code == 200
        assert response.json() == None