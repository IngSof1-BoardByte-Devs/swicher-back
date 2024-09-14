# Mocking the test_client to test the get_games endpoint

from fastapi.testclient import TestClient
from test.test_main import app_test
from unittest.mock import patch


client = TestClient(app=app_test)

@patch("app.routes.game.get_games")
def test_get_games(mock_get_games):
    # Define some mock games to return
    mock_games = [
        {"id": 1, "name": "Game 1", "players": ["Player 1", "Player 2"]},
        {"id": 2, "name": "Game 2", "players": ["Player 3", "Player 4"]}
    ]

    # Configure the mock to return the mock games
    mock_get_games.return_value = mock_games

    # Call the endpoint
    response = client.get("/game/get_games")

    # Assert that the status code is 200
    assert response.status_code == 200

    # Assert that the returned games match the mock games
    assert response.json() == mock_games

def test_get_games():
    response = client.get("/game/get_games")
    assert response.status_code == 200
    assert response.json() == []
