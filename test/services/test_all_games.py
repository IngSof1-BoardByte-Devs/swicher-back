from unittest.mock import MagicMock
import pytest

from app.schemas.game import GameOut
from app.services.game import GameService


class TestAllGames:
    def mock_fetch_games(options):
        games = []
        if options == 1:
            #Partidas genericas
            games.extend(
                MagicMock(id=i, players=list(range(1, i+1)), started=False)
                for i in range(1, 4))
            # Asignar los nombres por separado debido al conflicto con MagicMock
            for i in range(len(games)):
                games[i].name = f"Juego {i+1}"
            #Partida empezada
            games.append(MagicMock(id=4,players=[1,2],started=True))
            games[3].name="Juego empezado"
            #Partida llena
            games.append(MagicMock(id=5,players = [1,2,3,4],started=False))
            games[4].name="Juego lleno"
        return games
    
    def expected(options):
        result = []
        if options == 1:
            result.extend(
                GameOut(
                    id=i,
                    name=f"Juego {i}",
                    num_players=i)
                for i in range(1, 4))
            result.append(GameOut(id=5,name="Juego lleno",num_players=4))
        return result
            

    @pytest.mark.parametrize("fetch_games, expected_return", [
        #Caso normal
        (mock_fetch_games(1),expected(1)),
        #Caso vacío
        (mock_fetch_games(2),expected(2))
    ])
    def test_get_all_games(self, mocker, fetch_games, expected_return):

        #Mock cruds
        mock_fetch_games = mocker.patch("app.services.game.fetch_games")

        #Config cruds
        mock_fetch_games.return_value = fetch_games

        #Instancia db
        instance = GameService(db=MagicMock())
        result = instance.get_all_games()
        assert result == expected_return

        #Verificaciones
        mock_fetch_games.assert_called_once_with(instance.db)