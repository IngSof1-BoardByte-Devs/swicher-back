from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.schemas.game import *
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.models import Base, Game, Player

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

def mock_get_player_by_id(*args, **kwargs):
    player_id = kwargs.get('player_id', None)
    if player_id == 1:
        return Player(id=1, username="Jugador 1", game_id=1)

def test_leave_game():
    # Crear un juego con un jugador(host)
    mock_game = Game(id=1, name="test_game")
    # Crear un jugador
    mock_player1 = Player(id=1, username="test_player", game_id=1)
    leave_game_request = LeaveStartGame(player_id=1, game_id=1)

    with patch('app.services.game.GameService.leave_game', return_value=None),\
        patch('app.services.game.get_game_by_id', return_value=mock_game),\
        patch('app.services.game.get_player_by_id', return_value=mock_player1):
        response = client.post("/game/leave_game",  json=leave_game_request.model_dump())
        assert response.status_code == 200
        assert response.json() == None

def test_leave_game_not_found():
    leave_game_request = LeaveStartGame(player_id=1, game_id=5)

    with patch('app.services.game.get_game_by_id', return_value=None),\
        patch('app.services.game.get_player_by_id', return_value=None):
        response = client.post("/game/leave_game", json=leave_game_request.model_dump())
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid player or game"}
