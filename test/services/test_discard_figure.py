import json
from unittest.mock import MagicMock
import pytest

from app.schemas.figure import FigUpdate
from app.services.figures import FigureService
from app.utils.enums import FigureStatus

@pytest.mark.asyncio
class TestDiscardFigure:
    def mock_websocket(self, ws, json_ws):
        ws.context = json_ws
    
    def mock_get_figures_hand(self,player):
        return [figure for figure in player.figures]

    @pytest.mark.parametrize("win, websocket_return", [
        #Caso normal sin ganador
        (False,None),
        #Caso normal con ganador
        (True,json.dumps({"event": "game.winner", "payload": {"player_id": 3}}))    
    ])
    async def test_discard_figure(self, mocker, win, websocket_return):
        #Mock cruds
        mock_get_figures_hand = mocker.patch("app.services.figures.get_figures_hand")
        mock_get_figures_deck = mocker.patch("app.services.figures.get_figures_deck")
        mock_websocket = mocker.patch("app.services.figures.manager.broadcast")
        mock_delete_all_game = mocker.patch("app.services.figures.delete_all_game")
        

        #Config cruds
        mock_get_figures_hand.side_effect = lambda _, player: self.mock_get_figures_hand(player)
        mock_get_figures_deck.return_value = []

        #Instancia db
        db = MagicMock()
        db.players = []
        db.figures = []
        db.games = []
        db.games.extend(MagicMock(id=i+1,partial_movements=[]) for i in range(2))

        #Caso 1
        db.players.extend(MagicMock(id=i+1,turn=i+1,figures=[]) for i in range(2))
        db.figures.extend(MagicMock(id=i+1,player=db.players[0],status=FigureStatus.INHAND) for i in range(2))
        db.players[0].figures.extend(db.figures[i] for i in range(2))
        
        #Caso 2
        db.players.extend(MagicMock(id=i+3,turn=i+1,figures=[]) for i in range(2))
        db.figures.append(MagicMock(id=3,player=db.players[2],status=FigureStatus.INHAND))
        db.players[2].figures.append(db.figures[2])

        #Instancia websocket
        ws = MagicMock()
        ws.context = None
        
        mock_websocket.side_effect = lambda json_sw, _: self.mock_websocket(ws,json_sw)
        
        instance = FigureService(db)
        
        figure = None
        player = None
        game = None
        if win:
            figure = db.figures[2]
            player = db.players[2]
            game = db.game[1]
        else:
            figure = db.figures[0]
            player = db.players[0]
            game = db.game[0]

        await instance.discard_figure(figure,player,game)

        #Verificaciones
        assert ws.context == websocket_return
        if win:
            mock_delete_all_game.assert_called_once_with(db,game)
        else:
            assert len(player.figures)==1
