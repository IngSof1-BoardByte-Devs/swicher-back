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
        figures = []
        for figure in player.figures:
            if figure.status == FigureStatus.INHAND:
                figures.append(figure)
        return figures
    
    def mock_get_figures_deck(self,player):
        figures = []
        for figure in player.figures:
            if figure.status == FigureStatus.INDECK:
                figures.append(figure)
        return figures
    
    def mock_has_blocked_figures(self,player):
        return any(figure.status == FigureStatus.BLOCKED for figure in player.figures)

    @pytest.mark.parametrize("figure_id, player_id, websocket_return, exception", [
        #Caso normal sin ganador
        (1,1,None,None),
        #Caso normal con ganador
        (3,2,json.dumps({"event": "game.winner", "payload": {"player_id": 2}}),None),
        #Caso normal una figura bloqueada
        (4,3,None,None),
        #Caso error figura bloqueada y mas cartas
        (6,4,None,Exception("El jugador no puede descartar una carta bloqueada")),

    ])
    async def test_discard_figure(self, mocker, figure_id, player_id, websocket_return, exception):
        #Mock cruds
        mock_get_figures_hand = mocker.patch("app.services.figures.get_figures_hand")
        mock_get_figures_deck = mocker.patch("app.services.figures.get_figures_deck")
        mock_websocket = mocker.patch("app.services.figures.manager.broadcast")
        mock_delete_all_game = mocker.patch("app.services.figures.delete_all_game")
        mock_has_blocked_figures = mocker.patch("app.services.figures.has_blocked_figures")
        

        #Config cruds
        mock_get_figures_hand.side_effect = lambda _, player: self.mock_get_figures_hand(player)
        mock_get_figures_deck.side_effect = lambda _, player: self.mock_get_figures_deck(player)
        mock_has_blocked_figures.side_effect = lambda _, player: self.mock_has_blocked_figures(player)

        #Instancia db
        db = MagicMock()
        db.players = []
        db.figures = []
        db.game = MagicMock(id=1,partial_movements=[])
        db.players.extend(MagicMock(id=i+1,figures=[]) for i in range(4))

        #Jugador 1
        db.figures.extend(MagicMock(id=i+1,player=db.players[0],status=FigureStatus.INHAND) for i in range(2))
        db.players[0].figures.extend(db.figures[i] for i in range(2))

        #Jugador 2
        db.figures.append(MagicMock(id=3,player=db.players[1],status=FigureStatus.INHAND))
        db.players[1].figures.append(db.figures[2])

        #Jugador 3
        db.figures.append(MagicMock(id=4,player=db.players[2],status=FigureStatus.BLOCKED))
        db.figures.append(MagicMock(id=5,player=db.players[2],status=FigureStatus.INDECK))
        db.players[2].figures.extend(db.figures[i+3] for i in range(2))

        #Jugador 4
        db.figures.append(MagicMock(id=6,player=db.players[3],status=FigureStatus.BLOCKED))
        db.figures.append(MagicMock(id=7,player=db.players[3],status=FigureStatus.INHAND))
        db.players[3].figures.extend(db.figures[i+5] for i in range(2))

        #Instancia websocket
        ws = MagicMock()
        ws.context = None
        
        mock_websocket.side_effect = lambda json_sw, _: self.mock_websocket(ws,json_sw)
        
        instance = FigureService(db)

        
        if isinstance(exception, Exception):
            with pytest.raises(Exception, match=str(exception)):
                await instance.discard_figure(db.figures[figure_id-1],db.players[player_id-1],db.game)
        else:
            await instance.discard_figure(db.figures[figure_id-1],db.players[player_id-1],db.game)

            #Verificaciones
            assert ws.context == websocket_return
            if websocket_return != None:
                mock_delete_all_game.assert_called_once_with(db,db.game)
            else:
                assert len(db.players[player_id-1].figures)==1
