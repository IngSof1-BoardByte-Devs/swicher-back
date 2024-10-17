from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import RevertRequest

class TestRevertMoves:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("game_id, revert_request, service_return, expected_status, expected_response", [
        # Caso normal
        (1,
         RevertRequest(player_id=1),
         None,  # No se devuelve nada de GameService.revert_moves
         200,
         {"message": "Turn reverted successfully"}
        ),
        # Caso existencial
        (2,
         RevertRequest(player_id=1),
         Exception("No hay cambios para revertir"),
         404,
         {"detail": "No hay cambios para revertir"}
         ),
         # Caso excepcional
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
    async def test_revert_moves(self, mocker, game_id, 
                               revert_request, service_return, 
                               expected_status, expected_response):
        # Cliente
        client = TestClient(app)
        
        async def mock_revert_moves(*args, **kwargs):
                    if isinstance(service_return, Exception):
                        raise service_return
                    return None
        mocker.patch("app.routes.game.MoveService.revert_moves", side_effect=mock_revert_moves)
        
        response = client.patch(f"games/{game_id}/revert-moves", json=revert_request.model_dump())
        assert response.status_code == expected_status
        assert response.json() == expected_response