from app.schemas.game import JoinGame
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Game, Player

client = TestClient(app)

# Fixture para la sesión de la base de datos en memoria
@pytest.fixture(scope="module")
def db_session():
    engine = create_engine('sqlite:///:memory:')  # Crea una base de datos SQLite en memoria
    Base.metadata.create_all(engine)  # Crea las tablas en la base de datos
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session  # Esta es la sesión que tus pruebas usarán
    session.close()

# Test para unirse a un juego con éxito
def test_join_game_success(db_session):
    mock_game = Game(id=1, name="test_game")
    mock_player = Player(id=1, username="test_player", game_id=1)
    game_data = JoinGame(game_id=1, player_name="test_player")


    # Simular la operación de la base de datos, en vez de ejecutarse las operaciones crud se remplazan por las funciones de simulación
    with patch('app.services.game.get_game', return_value= mock_game), \
        patch('app.services.game.create_player', return_value=mock_player):
        response = client.post("/players/", json=game_data.model_dump())
        assert response.status_code == 200
        assert response.json() == {'player_id': 1,'game_id': 1}


# Test para unirse a un juego con un ID de juego inválido
def test_join_game_invalid_game_id(db_session):
    game_data = JoinGame(game_id=-1, player_name="Jugador 1")
    mock_game = None

    with patch('app.services.game.get_game', return_value= mock_game):
        response = client.post("/players/", json=game_data.model_dump())
        assert response.status_code == 400
        assert response.json() == {'detail': {'message': 'Error: User tries to join a non-existent game', 'status': 'ERROR'}}


def mock_player_error(*args, **kwargs):
    raise ValueError("Invalid arguments")