import json
from unittest.mock import MagicMock
import pytest

from app.services.game import GameService

"""Concentrado en ver como quedan los turnos despues de que abandone el jugador"""

@pytest.mark.asyncio
class TestLeaveGame:
    def mock_get_player(self, db, player_id):
        return next((p for p in db.players if p.id == player_id), None)
    
    def mock_get_game_by_player_id(self, db, player_id):
        return next((g for g in db.games if self.mock_get_player(db,player_id) in g.players), None)

    def mock_delete(self,db,mock):
        if mock.type == "player":
            db.players.remove(mock)
        elif mock.type == "game":
            db.games.remove(mock)

    def mock_manager_broadcast(self,ws,json_ws):
        ws.result = json_ws


    @pytest.mark.parametrize("player_id, started, turn, expected_turn, exception, expected_broadcast", [
        #Caso lobby sin ser el host
        (2,False,0,0,None,
         json.dumps({"event": "player.left", "payload": {"game_id": 1, "username": "player2"}})),
        #Caso lobby siendo el host
        (1,False,0,None,None,
         json.dumps({"event": "game.cancelled", "payload": {"game_id": 1}})),
        #Caso game ultimo jugador sin ser su turno
        (4,True,3,3,None,
         json.dumps({"event": "player.left", "payload": {"game_id": 1, "username": "player4"}})),
        #Caso game ultimo jugador siendo su turno
        (4,True,4,1,None,
         json.dumps({"event": "player.left", "payload": {"game_id": 1, "username": "player4"}})),
        #Caso game siendo primer jugador sin ser turno
        (1,True,2,1,None,
         json.dumps({"event": "player.left", "payload": {"game_id": 1, "username": "player1"}})),
        #Caso game quede un solo jugador
        (5,True,2,None,None,
         json.dumps({"event": "game.winner", "payload": {"player_id": 6}})),
        #Caso que no encuentra al jugador
        (7,None,None,None,Exception("Jugador no encontrado"),None),
    ])
    async def test_leave_game(self, mocker, player_id, started, turn, expected_turn, exception, expected_broadcast):

        #Instancia db
        db = MagicMock(players=[],games=[],ws=MagicMock(result=None))
        #Jugadores
        db.players.extend(MagicMock(id=i,username=f"player{i}",type="player",movements=[],figures=[]) for i in range(1,7))
        for i in range(4): db.players[i].turn = i+1
        for i in range(4,6): db.players[i].turn = i-3
        #Juegos
        db.games.extend(MagicMock(id=i,turn=turn,started=started,players=[],type="game", movements=[],
                                  figures=[],partial_movements=[]) for i in range(1,3))
        db.games[0].players.extend(db.players[i] for i in range(4))
        db.games[0].host = db.players[0]
        db.games[1].players.extend(db.players[i] for i in range(4,6))
        db.games[1].host = db.players[4]

        #Mock cruds
        mock_get_player = mocker.patch("app.services.game.get_player")
        mock_get_game_by_player_id = mocker.patch("app.services.game.get_game_by_player_id")
        mock_manager_broadcast = mocker.patch("app.services.game.manager.broadcast")

        #Config cruds
        mock_get_player.side_effect = lambda db, player_id: self.mock_get_player(db, player_id)
        mock_get_game_by_player_id.side_effect = lambda db, player_id: self.mock_get_game_by_player_id(
            db, player_id)
        mock_manager_broadcast.side_effect = lambda json_ws, _: self.mock_manager_broadcast(db.ws,json_ws)
        db.delete.side_effect = lambda mock: self.mock_delete(db,mock)

        #Instancia
        instance = GameService(db)
        if isinstance(exception, Exception):
            with pytest.raises(Exception, match=str(exception)):
                await instance.leave_game(player_id)
        else:
            await instance.leave_game(player_id)

            #Verificaciones
            #Caso de juegos no eliminados
            if expected_turn is not None:
                game = db.games[0]
                assert game.turn == expected_turn
                assert len(game.players) == 3
                assert len(db.players) == 5
                if started: assert all(game.players[i].turn == i+1 for i in range(len(game.players)))
            #Caso de juego eliminado
            else:
                assert len(db.games) == 1
            #Websocket
            assert db.ws.result == expected_broadcast