from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.movement import Movement, MovementPartial
from app.utils.enums import MovementType

client = TestClient(app)

class TestPatchMove:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("id, movement_request, service_return, expected_status, expected_response", [
        # Caso normal
        (1,
         MovementPartial(playerId=1, index1=7, index2=8),
         Movement(card_id=1, id_player=1, type=MovementType.TYPE1),
         200,
         {"msg": "Carta usada con éxito"}
        ),
        # Caso existencial
        (2,
         MovementPartial(playerId=1, index1=7, index2=8),
         Exception("La carta de movimiento no existe"),
         404,
         {"detail": "La carta de movimiento no existe"}
         ),
         # Caso no autorizado
        (3,
         MovementPartial(playerId=1, index1=7, index2=8),
         Exception("La carta no te pertenece"),
         401,
         {"detail": "La carta no te pertenece"}
         ),
         # Caso no válido para el movimiento
        (4,
         MovementPartial(playerId=1, index1=7, index2=8),
         Exception("La carta no es válida para ese movimiento"),
         401,
         {"detail": "La carta no es válida para ese movimiento"}
         ),
         # Caso error del servidor
        (5,
         MovementPartial(playerId=1, index1=7, index2=8),
         Exception("Internal server error"),
         500,
         {"detail": "Internal server error"}
        )
    ])
    async def test_use_movement_card(self, mocker, id, movement_request, service_return, expected_status, expected_response):
        # Definir un mock asíncrono para la función set_parcial_movement en MoveService
        async def mock_set_parcial_movement(*args, **kwargs):
            if isinstance(service_return, Exception):
                raise service_return
            return None
        
        # Aplicar el mock con side_effect para el método asíncrono
        mock_move_service = mocker.patch("app.routes.movement_card.MoveService.set_parcial_movement", side_effect=mock_set_parcial_movement)

        # Realizar la solicitud de prueba al endpoint
        response = client.put(f"movement-cards/{id}/status", json=movement_request.model_dump())

        # Verificar que el código de estado y la respuesta sean los esperados
        assert response.status_code == expected_status
        assert response.json() == expected_response
