import json
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.figure import FigUpdate, FigureDiscard

client = TestClient(app)

class TestGetMovements:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("id, playerID, service_return, expected_status, expected_response", [
        # Caso normal
        (1, FigureDiscard(playerId=1),
         FigUpdate(id=1, id_player=1, type="Type 1", discarded=True, blocked=False),
         200,
         {"msg": "Carta usanda con exito"}
        ),
        # Caso con error carta de figura no existe
        (10, FigureDiscard(playerId=1),
         Exception("La carta de figura no existe"),
         404,
         {"detail": "La carta de figura no existe"}
        ),
        # Caso con error carta/jugador no pertenece a este juego
        (1, FigureDiscard(playerId=3),
         Exception("La carta/jugador no pertenece a este juego"),
         401,
         {"detail": "La carta/jugador no pertenece a este juego"}
        ),
        # Caso con error carta debe estar en la mano
        (2, FigureDiscard(playerId=1),
         Exception("La carta debe estar en la mano"),
         400,
         {"detail": "La carta debe estar en la mano"}
        ),
        # Caso con error no es tu turno
        (3, FigureDiscard(playerId=2),
         Exception("No es tu turno"),
         403,
         {"detail": "No es tu turno"}
        ),
        # Caso con error función de bloquear figura no implementada
        (3, FigureDiscard(playerId=1),
         Exception("Función de bloquear figura no implementada"),
         501,
         {"detail": "Función de bloquear figura no implementada"}
        ),
        # Caso excepcional
        (1, FigureDiscard(playerId=1),
         Exception("Internal server error"),
         500,
         {"detail": "Internal server error"}
        )
    ])
    async def test_recognize_figure(self, mocker, id, playerID, service_return, expected_status, expected_response):
        # Crear el mock asíncrono para el método update_figure_status en FigureService
        async def mock_update_figure_status(*args, **kwargs):
            if isinstance(service_return, Exception):
                raise service_return
            return None
        
        # Aplicar el mock a FigureService.update_figure_status
        mocker.patch("app.routes.figure_card.FigureService.update_figure_status", side_effect=mock_update_figure_status)

        # Hacer la solicitud de prueba al endpoint
        response = client.put(f"/figure-cards/{id}/status", json=playerID.model_dump())

        # Verificar que el código de estado y la respuesta sean los esperados
        assert response.status_code == expected_status
        assert response.json() == expected_response
