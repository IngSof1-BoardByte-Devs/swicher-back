import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.game import CreateGame
from app.services.game import GameService

@pytest.fixture
def client():
    return TestClient(app)

def mock_create_game_service(self, game_data):
    # Mockear la respuesta del servicio
    return {"status": "OK", "game_id": 1}

def test_create_game_endpoint(client, monkeypatch):
    # Stubbing: Crear datos para el usuario
    game_data = CreateGame(player_name="Juan", game_name="Mi juego")

    # Mocking: Mockear el servicio
    monkeypatch.setattr(GameService, "create_game", mock_create_game_service)

    # Enviar solicitud al endpoint
    response = client.post("/game/create-game", json=game_data.dict())

    # Verificar respuesta
    assert response.status_code == 200
    assert response.json() == {"status": "OK", "game_id": 1}
    print(response.json())