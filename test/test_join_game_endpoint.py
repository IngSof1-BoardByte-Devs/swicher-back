from app.schemas.game import JoinGame
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

# Funciones de simulación de las operaciones de la base de datos
def mock_get_game_by_id(*args, **kwargs):
    game_id = kwargs.get('game_id', None)
    if game_id == 1:
        return Game(id=1, name="Juego 1")

def mock_create_player(*args, **kwargs):
    username = kwargs.get('username', None)
    game = kwargs.get('game', None)
    return {"username": username, "game": game}



# Test para unirse a un juego con éxito
def test_join_game_success(db_session):
    game_data = JoinGame(game_id=1, player_name="Jugador 1")

    # Simular la operación de la base de datos, en vez de ejecutarse las operaciones crud se remplazan por las funciones de simulación
    with patch('app.services.game.get_game', new=mock_get_game_by_id), \
        patch('app.services.game.create_player', new=mock_create_player):
        response = client.post("/game/join-game", json=game_data.model_dump())
        assert response.status_code == 200
        assert response.json() == [{'status': 'OK'}, 201]

# Test para unirse a un juego con un ID de juego inválido
def test_join_game_invalid_game_id(db_session):
    game_data = JoinGame(game_id=-1, player_name="Jugador 1")

    with patch('app.database.crud.get_game', return_value=None):
        response = client.post("/game/join-game", json=game_data.model_dump())
        assert response.status_code == 400
        assert response.json() == {'detail': {'message': 'ID de juego inválido', 'status': 'ERROR'}}

# Test para unirse a un juego con un nombre de jugador vacío
def test_join_game_empty_player_name(db_session):
    game_data = JoinGame(game_id=1, player_name="")

    with patch('app.database.crud.get_game', new=mock_get_game_by_id):
        response = client.post("/game/join-game", json=game_data.model_dump())
        assert response.status_code == 400
        assert response.json() == {'detail': {'message': 'Nombre de jugador requerido', 'status': 'ERROR'}}