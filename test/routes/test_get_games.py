# test/test_getGames.py
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.schemas.game import GameOut

client = TestClient(app)

def test_get_games():
    mock_game = GameOut(id=1, name="test_game", num_players=0)

    with patch('app.services.game.GameService.get_all_games', return_value=[mock_game]):
        response = client.get("/games/")
        assert response.status_code == 200
        assert response.json() == [mock_game.model_dump()]

def test_get_games_empty():
    with patch('app.services.game.GameService.get_all_games', return_value=[]):
        response = client.get("/games/")
        assert response.status_code == 200
        assert response.json() == []

def test_get_games_whit_error():
    with patch('app.services.game.GameService.get_all_games', side_effect=Exception("Test error")):
        response = client.get("/games/")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal server error"}