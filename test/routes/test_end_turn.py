from fastapi.testclient import TestClient
import pytest
from app.main import app


class TestGetMovements:

    @pytest.mark.parametrize("id_player, service_return,expected_status, expected_response", [
        #Caso normal
        (1, None, 200, {"status": "OK", "message": "Turn ended"}),
        #Caso con error de partida no iniciada
        (2, Exception("Partida no iniciada"), 400,{"detail": "Partida no iniciada"}),
        #Caso con error de no ser el turno del jugador
        (3, Exception("No es turno del jugador"), 401,{"detail": "No es turno del jugador"}),
        #Caso con error de no encontrarse el jugador
        (4, Exception("Jugador no encontrado"), 404,{"detail": "Jugador no encontrado"}),
        #Caso excepcional
        (1, Exception("Internal server error"),500, {"detail": "Internal server error"})
    ])
    def test_end_turn(self, mocker, id_player, service_return,expected_status, expected_response):
        #Cliente
        client = TestClient(app)

        mock_end_turn = mocker.patch("app.routes.player.GameService.change_turn")

        if isinstance(service_return, Exception):
            mock_end_turn.side_effect = service_return

        response = client.put(f"/players/{id_player}/turn")

        assert response.status_code == expected_status
        assert response.json() == expected_response