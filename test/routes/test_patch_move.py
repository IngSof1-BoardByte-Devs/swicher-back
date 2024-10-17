from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.movement import Movement, MovementPartial
from app.utils.enums import MovementType



class TestPatchMove:


    @pytest.mark.parametrize("card_id, movement_request, service_return, expected_status, expected_response", [
        # Caso normal
        (1,
         MovementPartial(playerId = 1, index1=7, index2=8),
         Movement( card_id= 1, id_player= 1, type= MovementType.TYPE1),
         200,
         {"card_id": 1, "id_player": 1,"type": "Type 1"}
        ),
        # Caso existencial
        (2,
         MovementPartial(playerId = 1, index1=7, index2=8),
         Exception("La carta de movimiento no existe"),
         404,
         { "detail" : "La carta de movimiento no existe" }
         ),
         # Caso excepcional
        (3,
         MovementPartial(playerId = 1, index1=7, index2=8),
         Exception("La carta no te pertenece"),
         401,
         { "detail" : "La carta no te pertenece"}
         ),
         # Caso excepcional
        (4,
         MovementPartial(playerId = 1, index1=7, index2=8),
         Exception("La carta no es válida para ese movimiento"),
         401,
         { "detail" : "La carta no es válida para ese movimiento"}
         ),
         # Caso error server
        (5,
         MovementPartial(playerId = 1, index1=7, index2=8),
         Exception("Internal server error"),
         500,
         {"detail": "Internal server error"}
        )
    ])
    def test_use_movement_card(self, mocker, card_id, 
                               movement_request, service_return, 
                               expected_status, expected_response):
        # Cliente
        client = TestClient(app)
        

        mock_move_service = mocker.patch("app.routes.movement_card.MoveService.set_parcial_movement")


        if isinstance(service_return, Exception):
            mock_move_service.side_effect = service_return
        else:
            mock_move_service.return_value = service_return

        response = client.patch(f"/movement-cards/{card_id}/", json=movement_request.model_dump())

        assert response.status_code == expected_status
        assert response.json() == expected_response