from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.game import RevertRequest

class TestRevertMoves:
    @pytest.mark.parametrize("game_id, revert_request, service_return, expected_status, expected_response", [
        # Caso normal
        (1,
         RevertRequest(player_id=1),
         {"message": "Turn reverted successfully"},
         200,
         {"message": "Turn reverted successfully"}
        ),
        # Caso existencial
        (2,
         RevertRequest(player_id=1),
         Exception("Partida no encontrada"),
         404,
         {"detail": "Partida no encontrada"}
         ),
         # Caso excepcional
        (3,
         RevertRequest(player_id=1),
         Exception("Jugador no encontrado"),
         401,
         {"detail": "Jugador no encontrado"}
         ),
         # Caso error server
        (4,
         RevertRequest(player_id=1),
         Exception("Internal server error"),
         500,
         {"detail": "Internal server error"}
        )
    ])
    def test_revert_moves(self, mocker, game_id, 
                               revert_request, service_return, 
                               expected_status, expected_response):
        # Cliente
        client = TestClient(app)
        
        mock_revert_moves = mocker.patch("app.routes.game.GameService.revert_moves")
        if isinstance(service_return, Exception):
            mock_revert_moves.side_effect = service_return
        else:
            mock_revert_moves.return_value = service_return
        response = client.patch(f"/games/{game_id}/revert-moves", json=revert_request.model_dump())
        assert response.status_code == expected_status
        assert response.json() == expected_response