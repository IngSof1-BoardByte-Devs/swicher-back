from unittest.mock import MagicMock
import pytest

from app.schemas.game import PlayerAndGame
from app.services.movement import MoveService
from app.utils.enums import MovementStatus


class TestRevertMoves:
    def board_default(self):
        return [i + 1 for i in range(36)]
    
    def mock_get_player(self,db,player_id):
        return next((p for p in db.players if p.id == player_id), None)

    def mock_get_game(self,db,game_id):
        game = None

        if game_id in range(1,6):
            game = MagicMock(id = game_id, turn = 1)
            game.started = game_id != 4

            #Jugadores
            players = {
                1: [self.mock_get_player(db,1),self.mock_get_player(db,10)],
                2: [self.mock_get_player(db,2), 20],
                3: [self.mock_get_player(db,3), 30, 31],
                4: [self.mock_get_player(db,4)],
                5: [self.mock_get_player(db,5),51]
            }
            game.players = players[game_id]

            #Tablero
            game.board_matrix = self.board_default() if game_id != 4 else []

            #Movimientos parciales
            if game_id not in [4,5]:
                game.partial_movements = [MagicMock(id = 1, x1=0, x2=1, y1=2, y2=3)]
                db.movs.append(MagicMock(id = 1, player = None,
                                        status = MovementStatus.DISCARDED))
                game.partial_movements[0].movement = db.movs[0]

                game.board_matrix[1] = 16
                game.board_matrix[15] = 2

                if game_id in [2,3]:
                    game.partial_movements.append(MagicMock(id = 2,x1=3,x2=1,y1=5,y2=2))
                    db.movs.append(MagicMock(id = 2, player = None,
                                            status = MovementStatus.DISCARDED))
                    game.partial_movements[1].movement = db.movs[1]

                    game.board_matrix[19] = 33
                    game.board_matrix[32] = 20

                    if game_id == 3:
                        game.partial_movements.append(MagicMock(id = 3,x1=5,x2=2,y1=5,y2=5))
                        db.movs.append(MagicMock(id = 3, player = None,
                                                status = MovementStatus.DISCARDED))
                        game.partial_movements[2].movement = db.movs[2]

                        game.board_matrix[32] = 36
                        game.board_matrix[35] = 20
            else:
                game.partial_movements = []

        db.game = game
        return game
    
    def mock_delete(self, db, partial_mov):
        db.game.partial_movements.remove(partial_mov)
    

    @pytest.mark.parametrize("data, expected_return", [
        #Caso normal un movimiento a revertir
        (PlayerAndGame(player_id=1,game_id=1),None),
        #Caso normal dos movimientos a revertir
        (PlayerAndGame(player_id=2,game_id=2),None),
        #Caso normal tres movimientos a revertir
        (PlayerAndGame(player_id=3,game_id=3),None),
        #Caso error partida no encontrada
        (PlayerAndGame(player_id=1,game_id=100), Exception("Partida no encontrada")),
        #Caso error partida no iniciada
        (PlayerAndGame(player_id=4,game_id=4), Exception("Partida no iniciada")),
        #Caso error sin cambios para revertir
        (PlayerAndGame(player_id=5,game_id=5), Exception("No hay cambios para revertir")),
        #Caso error jugador no encontrado
        (PlayerAndGame(player_id=100,game_id=1), Exception("Jugador no encontrado")),
        #Caso error jugador no pertenece a partida
        (PlayerAndGame(player_id=2,game_id=1), Exception("El jugador no pertenece a esta partida")),
        #Caso error jugador de otro turno
        (PlayerAndGame(player_id=10,game_id=1), Exception("No tienes autorización para revertir estos cambios")),
    ])
    def test_revert_moves(self, mocker, data, expected_return):

        #Mock cruds
        mock_get_game = mocker.patch("app.services.movement.get_game")
        mock_get_player = mocker.patch("app.services.movement.get_player")

        #Config cruds
        mock_get_game.side_effect = lambda db, game_id: self.mock_get_game(db,game_id)
        mock_get_player.side_effect = lambda db, player_id: self.mock_get_player(db,player_id)

        #Instancia db
        db = MagicMock()
        db.commit.return_value = None
        db.game = None
        db.movs = []
        db.players = []
        db.players.extend(MagicMock(id=player,turn = 1) for player in range(1,6))
        db.players.append(MagicMock(id=10,turn=2))
        
        db.delete.side_effect = lambda partial_mov: self.mock_delete(db,partial_mov)
        
        instance = MoveService(db)
        if isinstance(expected_return, Exception):
            with pytest.raises(Exception, match=str(expected_return)):
                instance.revert_moves(data)
            
        else:
            instance.revert_moves(data)

            #Verificaciones
            assert db.game.board_matrix == self.board_default()
            assert db.game.partial_movements == []
            assert all(mov.player.id == data.player_id for mov in db.movs)
            mock_get_game.assert_called_once_with(instance.db, data.game_id)
            mock_get_player.assert_called_once_with(instance.db, data.player_id)
