from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import GameLeaveCreateResponse, JoinGame


class TestGetMovements:

    @pytest.mark.parametrize("game_data, service_return, expected_status, expected_response", [
        #Caso normal
        (JoinGame(game_id=1,player_name="test"),
         GameLeaveCreateResponse(player_id=2, game_id=1),
         200, {"player_id": 2, "game_id": 1}),
        #Caso con error al enviar nombre vacio
        (JoinGame(game_id=1,player_name=""),
         Exception("El jugador debe tener un nombre"), 400,
         {"detail": "El jugador debe tener un nombre"}),
        #Caso con error al unirse a una partida iniciada 
        (JoinGame(game_id=2,player_name="test"),
         Exception("Partida ya iniciada"), 400,{"detail": "Partida ya iniciada"}),
        #Caso con error al unirse a una partida llena 
        (JoinGame(game_id=3,player_name="test"),
         Exception("Partida con máximo de jugadores permitidos"), 400,
         {"detail": "Partida con máximo de jugadores permitidos"}),
        #Caso con error al no encontrar la partida
        (JoinGame(game_id=4,player_name="test"),
         Exception("Partida no encontrada"), 404,{"detail": "Partida no encontrada"}),
        #Caso excepcional
        (JoinGame(game_id=1,player_name="test"),
         Exception("Internal server error"),500, {"detail": "Internal server error"})
    ])
    def test_join_game(self, mocker, game_data, service_return, expected_status, expected_response):
        #Cliente
        client = TestClient(app)

        mock_join_game = mocker.patch("app.routes.player.GameService.join_game")

        if isinstance(service_return, Exception):
            mock_join_game.side_effect = service_return
        else:
            mock_join_game.return_value = service_return

        response = client.post("/players/",json=game_data.model_dump())

        assert response.status_code == expected_status
        assert response.json() == expected_response