from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from app.main import app

class TestSendMessage:

    @pytest.mark.parametrize("player_id, message, expected_exception", [
        # Caso normal
        (1, {"message": "Message String"}, None),
        # Caso con error donde no se encuentra el jugador
        (11, {"message": "Message String"}, HTTPException(status_code=404, detail="Jugador no encontrado")),
        # Caso excepcional
        (111, {"message": "Message String"}, HTTPException(status_code=500, detail="Internal server error"))
    ])
    def test_send_message(self, mocker, player_id, message, expected_exception):
        # Cliente
        client = TestClient(app)

        # Respuesta esperada
        response_expected = {"message": "Message sent"}
        
        # Simula la función de send_message
        mock_send_message = mocker.patch("app.services.player.PlayerService.send_message")

        # Simulo la respuesta de ejemplo
        if player_id == 1:
            if not expected_exception:
                mock_send_message.return_value = response_expected
            else:
                mock_send_message.side_effect = Exception("Internal server error")
        elif player_id == 11:
            mock_send_message.side_effect = Exception("Jugador no encontrado")
        else:
            mock_send_message.side_effect = Exception("Internal server error")
        
        # Verifico si send_message devuelve error o no
        response = client.post(f"/chats/{player_id}", json=message)
        if expected_exception:
            assert response.status_code == expected_exception.status_code
            assert response.json() == {"detail": expected_exception.detail}  
        else:
            assert response.status_code == 200
            assert response.json() == {"message": "Message sent"}