import pytest
from app.services.game import JoinGameService
from app.schemas.game import JoinGame

@pytest.fixture
def join_game_service():
    return JoinGameService()


def test_join_game_success(join_game_service):
    game_data = JoinGame(game_id=1, player_name="Jugador 1")
    response = join_game_service.join_game(game_data)
    assert response["status"] == "OK"
    assert response["message"] == "Jugador unido a la partida con éxito"


def test_join_game_invalid_game_id(join_game_service):
    game_data = JoinGame(game_id=-1, player_name="Jugador 1")
    with pytest.raises(ValueError):
        join_game_service.join_game(game_data)


def test_join_game_empty_player_name(join_game_service):
    game_data = JoinGame(game_id=1, player_name="")
    with pytest.raises(ValueError):
        join_game_service.join_game(game_data)