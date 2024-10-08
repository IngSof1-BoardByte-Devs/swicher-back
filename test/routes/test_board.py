import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock
from app.main import app
from app.services.board import BoardService
from app.schemas.board import BoardOut, Color

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_board_service(mocker):
    mock_service = Mock(spec=BoardService)
    mocker.patch("app.routes.game.BoardService", return_value=mock_service)
    return mock_service

@pytest.mark.parametrize("game_id, service_return, expected_status, expected_response", [
    (1, BoardOut(board=[Color(color=i) for i in range(36)]), 200, {"board": [{"color": i} for i in range(36)]}),
    (2, Exception("Partida no iniciada"), 400, {"detail": "Partida no iniciada"}),
    (3, Exception("Partida no encontrada"), 404, {"detail": "Partida no encontrada"}),
    (1, Exception("Internal server error"), 500, {"detail": "Internal server error"}),
])
def test_get_board(client, mock_board_service, game_id, service_return, expected_status, expected_response):
    if isinstance(service_return, Exception):
        mock_board_service.get_board_values.side_effect = service_return
    else:
        mock_board_service.get_board_values.return_value = service_return

    response = client.get(f"/games/{game_id}/board")

    assert response.status_code == expected_status
    assert response.json() == expected_response

    mock_board_service.get_board_values.assert_called_once_with(game_id)