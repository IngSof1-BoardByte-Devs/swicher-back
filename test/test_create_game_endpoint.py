from app.schemas.game import CreateGame
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.schemas.game import GameOut
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.models import Base, Game

client = TestClient(app)

# Fixture para la sesión de la base de datos en memoria
@pytest.fixture(scope="module")
def db_session() -> Session:
    engine = create_engine('sqlite:///:memory:')  # Crea una base de datos SQLite en memoria
    Base.metadata.create_all(engine)  # Crea las tablas en la base de datos
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session  # Esta es la sesión que tus pruebas usarán
    session.close()

# Función de simulación de la operación de la base de datos
def mock_create_game_service(*args, **kwargs):
    # Mockear la respuesta del servicio
    return {"status": "OK", "game_id": 1}

def test_create_game_endpoint(db_session):
    # Stubbing: Crear datos para el usuario
    game_data = CreateGame(player_name="Juan", game_name="Mi juego")

    # Mocking: Mockear el servicio
    with patch('app.services.game.GameService.create_game', new=mock_create_game_service):
        # Enviar solicitud al endpoint
        response = client.post("/game/create-game", json=game_data.model_dump())

    # Verificar respuesta
    assert response.status_code == 200
    assert response.json() == [{"message": "Partida creada con éxito"}, 200]