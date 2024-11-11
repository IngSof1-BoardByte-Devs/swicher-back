from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.schemas.figure import FigureOut
from app.utils.enums import FigureType


class TestGetMovements:

    @pytest.mark.parametrize("id_game, expected_exception", [
        #Caso normal
        (1, None),
        #Caso con error de partida no iniciada
        (2, HTTPException(status_code=400, detail="Partida no iniciada")),
        #Caso con error de partida no encontrada
        (3, HTTPException(status_code=404, detail="Partida no encontrada")),
        #Caso excepcional
        (1, HTTPException(status_code=500, detail="Internal server error"))
    ])
    def test_get_figures(self, mocker, id_game, expected_exception):
        #Cliente
        client = TestClient(app)

        #Respuesta de base de datos
        response_expected = [FigureOut(player_id=1,id_figure=1,type_figure=FigureType.TYPE1, locked=False),
                             FigureOut(player_id=1,id_figure=2,type_figure=FigureType.TYPE2, locked=False),
                             FigureOut(player_id=1,id_figure=7,type_figure=FigureType.TYPE7, locked=False),
                             FigureOut(player_id=2,id_figure=9,type_figure=FigureType.TYPE9, locked=False),]

        #Simula la función de get_figures
        mock_get_figures = mocker.patch("app.services.figures.FigureService.get_figures")

        #Simulo la respuesta de get_figures
        if id_game == 1:
            if not expected_exception:
                mock_get_figures.return_value = response_expected
            else:
                mock_get_figures.side_effect = Exception("Internal server error")
        elif id_game == 2:
            mock_get_figures.side_effect = Exception("Partida no iniciada")
        else:
            mock_get_figures.side_effect = Exception("Partida no encontrada")


        #Verifico si get_figures devuelve error o no
        response = client.get(f"/games/{id_game}/figure-cards")
        if expected_exception:
            assert response.status_code == expected_exception.status_code
            assert response.json() == {"detail": expected_exception.detail}
        else:
            assert response.status_code == 200
            assert response.json() == [{"player_id": 1, "id_figure": 1, "type_figure": FigureType.TYPE1.value, "locked": False},
                                        {"player_id": 1, "id_figure": 2, "type_figure": FigureType.TYPE2.value, "locked": False},
                                        {"player_id": 1, "id_figure": 7, "type_figure": FigureType.TYPE7.value, "locked": False},
                                        {"player_id": 2, "id_figure": 9, "type_figure": FigureType.TYPE9.value, "locked": False}
                                        ]
