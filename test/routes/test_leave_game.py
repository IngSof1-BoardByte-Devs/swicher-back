from fastapi.testclient import TestClient
import pytest
from app.main import app


class TestGetMovements:

    @pytest.mark.parametrize("id_player, service_return, expected_status, expected_response", [
        #Caso normal
        (1,
         {"status": "OK", "message": "Player left the game"},
         200,
         {"status": "OK", "message": "Player left the game"}
        ),
        #Caso con error de jugador no encontrado
        (2, Exception("Jugador no encontrado"), 404, {"detail": "Jugador no encontrado"}),
        #Caso excepcional
        (1, Exception("Internal server error"), 500, {"detail": "Internal server error"})
    ])
    def test_leave_game(self, mocker, id_player, service_return, expected_status, expected_response):
        #Cliente
        client = TestClient(app)

        mock_leave_game = mocker.patch("app.routes.player.GameService.leave_game")

        if isinstance(service_return, Exception):
            mock_leave_game.side_effect = service_return
        else:
            mock_leave_game.return_value = service_return

        response = client.delete(f"/players/{id_player}")

        assert response.status_code == expected_status
        assert response.json() == expected_response