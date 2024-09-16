from fastapi.testclient import TestClient
from app.database.models import Game, Player
from test.test_main import app_test
from test.conftest import setup_database
from pony.orm import db_session

client = TestClient(app=app_test)

def test_get_empty_games(setup_database):
    response = client.get("/game/get_games")
    assert response.status_code == 200
    assert response.json() == []

def insert_test_games():
    with db_session:
        # Create a game
        game = Game(name="Test Game 1")
        
        # Create the players and assign them to the game
        player1 = Player(username="Player 2", game=game)
        player2 = Player(username="Player 1", game=game)
    
    print(game.players)

def test_get_games_from_db(setup_database):  # Include the fixture here
    # Insert test games
    insert_test_games()

    # Test the endpoint
    response = client.get("/game/get_games")
    assert response.status_code == 200
    # Assert que onsidere que el orden de los jugadores puede variar
    assert response.json() == [
        {
            "id": 1,
            "name": "Test Game 1",
            "players": ["Player 1", "Player 2"]
        }
    ] or response.json() == [
        {
            "id": 1,
            "name": "Test Game 1",
            "players": ["Player 2", "Player 1"]
        }
    ]