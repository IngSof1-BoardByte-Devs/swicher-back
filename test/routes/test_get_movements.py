from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.movement import MovementOut
from app.utils.enums import MovementType


class TestGetMovements:

    @pytest.mark.parametrize("player_id, service_return, expected_status, expected_response", [
        #Caso normal
        (1, 
         [MovementOut(id_movement = 1, type_movement=MovementType.TYPE1),
          MovementOut(id_movement = 3, type_movement=MovementType.TYPE3),
          MovementOut(id_movement = 4, type_movement=MovementType.TYPE4)],
         200, 
         [{"id_movement": 1, "type_movement": MovementType.TYPE1.value},
                    {"id_movement": 3, "type_movement": MovementType.TYPE3.value},
                    {"id_movement": 4, "type_movement": MovementType.TYPE4.value}]
         ),
        #Caso con error de partida no iniciada
        (2, Exception("Partida no iniciada"), 400, {"detail": "Partida no iniciada"}),
        #Caso con error de no encontrar al jugador
        (3, Exception("Jugador no encontrado"), 404, {"detail": "Jugador no encontrado"}),
        #Caso excepcional
        (1, Exception("Internal server error"), 500, {"detail": "Internal server error"})
    ])
    def test_get_movements(self, mocker, player_id, service_return, expected_status, expected_response):
        #Cliente
        client = TestClient(app)

        #Simula la función de get_movements
        mock_get_movements = mocker.patch("app.routes.game.MoveService.get_movements")

        #Simulo la respuesta de get_movements
        if isinstance(service_return, Exception):
            mock_get_movements.side_effect = service_return
        else:
            mock_get_movements.return_value = service_return

        #Verifico si get_movements devuelve error o no
        response = client.get(f"/games/{player_id}/move-cards")

        assert response.status_code == expected_status
        assert response.json() == expected_response