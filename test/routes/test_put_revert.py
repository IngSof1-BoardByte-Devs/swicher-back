from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import RevertRequest

class TestRevertMoves:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("id, revert_request, service_return, expected_status, expected_response", [
        # Caso normal
        (1,
         RevertRequest(player_id=1),
         None,  # No se devuelve nada de GameService.revert_moves
         200,
         { "msg" : "Movimientos revertidos" }
        ),
        # Caso existencial
        (2,
         RevertRequest(player_id=1),
         Exception("No hay cambios para revertir"),
         400,
         {"detail": "No hay cambios para revertir"}
         ),
         # Caso error de autorización
        (3,
         RevertRequest(player_id=1),
         Exception("No tienes autorización para revertir estos cambios"),
         401,
         {"detail": "No tienes autorización para revertir estos cambios"}
         ),
         # Caso error server
        (4,
         RevertRequest(player_id=1),
         Exception("Internal server error"),
         500,
         {"detail": "Internal server error"}
        )
    ])
    async def test_revert_moves(self, mocker, id, 
                                revert_request, service_return, 
                                expected_status, expected_response):
        # Cliente
        client = TestClient(app)
        
        # Definir un mock para la función revert_moves en MoveService
        async def mock_revert_moves(*args, **kwargs):
            if isinstance(service_return, Exception):
                raise service_return
            return None
        
        # Mockear la función revert_moves de MoveService
        mocker.patch("app.routes.game.MoveService.revert_moves", side_effect=mock_revert_moves)
        
        # Realizar la petición con el client.put en la ruta correcta
        response = client.put(f"games/{id}/revert-moves", json=revert_request.model_dump())
        
        # Verificar el status y el contenido de la respuesta
        assert response.status_code == expected_status
        assert response.json() == expected_response
