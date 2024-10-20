
from app.schemas.movement import *
from fastapi.testclient import TestClient
from app.main import app
import pytest
from app.schemas.movement import MovementPartial
from app.database.models import Base, Movement
from app.utils.enums import MovementStatus, MovementType

client = TestClient(app)


class TestUpdateMovementCard:

    @pytest.mark.parametrize("movement_data, service_return, expected_status, expected_response", [
        # Caso normal
        (MovementPartial(playerId=1, index1=1, index2=2),
         Movement(card_id=1, id_player=1, type=1),
         200,
         {"card_id": 1, "id_player": 1, "type": 1}
         ),
        # Caso con error
        (MovementPartial(playerId=1, index1=1, index2=2), 
         Exception("La carta de movimiento no existe"), 
         404, 
         {"detail": "La carta de movimiento no existe"}
         ),
        # Caso excepcional
        (MovementPartial(playerId=1, index1=1, index2=2), 
         Exception("Internal server error"), 
         500, 
         {"detail": "Internal server error"}
         )
    ])
    def test_update_movement_card(self, mocker, movement_data, service_return, expected_status, expected_response):
        client = TestClient(app)

        mock_update_movement = mocker.patch("app.routes.MoveService.update_movement")

        if isinstance(service_return, Exception):
            mock_update_movement.side_effect = service_return
        else:
            mock_update_movement.return_value = service_return

        response = client.patch("/movement-cards/1", json=movement_data.dict())

        assert response.status_code == expected_status
        assert response.json() == expected_response