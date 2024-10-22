import json
from unittest.mock import MagicMock
import pytest

from app.schemas.figure import FigUpdate
from app.services.figures import FigureService
from app.utils.enums import FigureStatus

@pytest.mark.asyncio
class TestUpdateFigureStatus:
    def mock_websocket(self, ws, json_ws):
        ws.context = json_ws
    
    def mock_get_player(self,db,player_id):
        return next((p for p in db.players if p.id == player_id), None)

    def mock_get_figure(self,db,figure_id):
        return next((f for f in db.figures if f.id == figure_id), None)

    @pytest.mark.parametrize("figure_id, player_id, expected_return, websocket_return", [
        #Caso normal
        (1,1,FigUpdate(id=1,id_player=1,type="Type 1",discarded=True,blocked=False),
         json.dumps({"event": "figure.card.used",
                     "payload": {"card_id": 1,"discarded": True,"locked": False}})
        ),
        #Caso error figura no encontrada
        (10,1,Exception("La carta de figura no existe"),None),
        #Caso error player de otro juego
        (1,3,Exception("La carta/jugador no pertenece a este juego"),None),
        #Caso error carta en deck
        (2,1,Exception("La carta debe estar en la mano"),None),
        #Caso error jugador de otro turno
        (3,2,Exception("No es tu turno"),None),
        #Caso error temporal intenta bloquear carta figura
        (3,1,Exception("Función de bloquear figura no implementada"),None)
        
    ])
    async def test_update_figure_status(self, mocker, figure_id,player_id, expected_return, websocket_return):

        #Mock cruds
        mock_get_figure = mocker.patch("app.services.figures.get_figure")
        mock_get_player = mocker.patch("app.services.figures.get_player")
        mock_websocket = mocker.patch("app.services.figures.manager.broadcast")
        mock_discard_figure = mocker.patch("app.services.figures.FigureService.discard_figure")

        #Config cruds
        mock_get_figure.side_effect = lambda db, figure_id: self.mock_get_figure(db,figure_id)
        mock_get_player.side_effect = lambda db, player_id: self.mock_get_player(db,player_id)
        

        #Instancia db
        db = MagicMock()
        #Games
        db.games = []
        db.games.extend(MagicMock(id=i+1,turn=1) for i in range(2))
        #Players
        db.players = []
        db.players.extend(MagicMock(id=i+1,turn=1) for i in range(3))
        db.players[0].game = db.games[0]
        db.players[1].game = db.games[0]
        db.players[1].turn = 2
        db.players[2].game = db.games[1]
        #Figuras
        db.figures = []
        db.figures.extend(MagicMock(id=i+1,status=FigureStatus.INHAND,type="Type 1") for i in range(3))
        db.figures[0].game = db.games[0]
        db.figures[0].player = db.players[0]
        db.figures[1].game = db.games[0]
        db.figures[1].player = db.players[0]
        db.figures[1].status = FigureStatus.INDECK
        db.figures[2].game = db.games[0]
        db.figures[2].player = db.players[1]
        

        #Instancia websocket
        ws = MagicMock()
        ws.context = None
        
        mock_websocket.side_effect = lambda json_sw, _: self.mock_websocket(ws,json_sw)
        
        instance = FigureService(db)
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                await instance.update_figure_status(figure_id,player_id)
            
        else:
            result = await instance.update_figure_status(figure_id,player_id)
            assert result == expected_return

            #Verificaciones
            assert ws.context == websocket_return
            mock_discard_figure.assert_called_once_with(db.figures[0],db.players[0],db.games[0])
