from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.schemas.game import *
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.database.models import Base, Game, Player

client = TestClient(app)

def test_leave_game():
    player_id = 1
    # Crear un juego con un jugador(host)
    mock_game = Mock()
    
    # Crear un jugador
    mock_player1 = Mock()
    mock_player1.id = player_id


    mock_game.players = [mock_player1]

    with patch('app.services.game.get_game_by_player_id', return_value=mock_game),\
        patch('app.services.game.get_player', return_value=mock_player1),\
        patch('app.services.game.delete_player', return_value=None),\
        patch('app.services.game.manager.broadcast', return_value=None),\
        patch('app.services.game.delete_all_game', return_value=None):
        response = client.delete(f"/players/{player_id}")
        assert response.status_code == 200

def test_leave_player_not_found():
    player_id = 1
    mock_game = Mock()

    with patch('app.services.game.get_game_by_player_id', return_value = mock_game),\
        patch('app.services.game.get_player', return_value=None),\
        patch('app.services.game.delete_player', return_value=None),\
        patch('app.services.game.manager.broadcast', return_value=None),\
        patch('app.services.game.delete_all_game', return_value=None):
        response = client.delete(f"/players/{player_id}")
        assert response.status_code == 400
        assert response.json() == {'detail': {'message': '404: Player not found', 'status': 'ERROR'}}
