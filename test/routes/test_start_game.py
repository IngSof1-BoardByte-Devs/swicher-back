from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from app.main import app


class TestGetMovements:

    @pytest.mark.parametrize("player_id, expected_exception", [
        #Caso normal
        (1, None),
        #Caso con error donde ya se inició la partida
        (11,
            HTTPException(status_code=400, detail="La partida ya se inició")),
        #Caso con error donde hay menos de 2 jugadores
        (111,
            HTTPException(status_code=400, detail="La partida debe tener entre 2 a 4 jugadores para iniciar")),
        #Caso con error donde el dueño no es quien inicializa la partida
        (1111,
            HTTPException(status_code=401, detail="Sólo el dueño puede iniciar la partida")),
        #Caso con error donde no se encuentra el jugador
        (11111,
            HTTPException(status_code=404, detail="Jugador no encontrado")),
        #Caso excepcional
        (1, HTTPException(status_code=500, detail="Internal server error"))
    ])
    def test_start_game(self, mocker, player_id, expected_exception):
        #Cliente
        client = TestClient(app)

        #Respuesta de base de datos
        response_expected = {"msg" : "Juego iniciado"}
        
        #Simula la función de start_game
        mock_start_game = mocker.patch("app.services.game.GameService.start_game")

        #Simulo la respuesta de ejemplo
        if player_id == 1:
            if not expected_exception:
                mock_start_game.return_value = response_expected
            else:
                mock_start_game.side_effect = Exception("Internal server error")
        elif player_id == 11:
            mock_start_game.side_effect = Exception("La partida ya se inició")
        elif player_id == 111:
            mock_start_game.side_effect = Exception("La partida debe tener entre 2 a 4 jugadores para iniciar")
        elif player_id == 1111:
            mock_start_game.side_effect = Exception("Sólo el dueño puede iniciar la partida")
        else:
            mock_start_game.side_effect = Exception("Jugador no encontrado")
        
        
        #Verifico si start_game devuelve error o no
        response = client.put("/games/{id}/started")
        if expected_exception:
            assert response.status_code == expected_exception.status_code
            assert response.json() == {"detail": expected_exception.detail}  
        else:
            assert response.status_code == 200
            assert response.json() == {"msg" : "Juego iniciado"}

