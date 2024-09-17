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