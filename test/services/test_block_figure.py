import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.figures import FigureService

class TestBlockFigure(unittest.IsolatedAsyncioTestCase):
    
    @patch('app.services.figures.has_blocked_figures')
    @patch('app.services.figures.get_figures_hand')
    @patch('app.services.figures.block_figure_status')
    async def test_block_figure(self, mock_block_figure_status, mock_get_figures_hand, mock_has_blocked_figures):
        # Crea un jugador y una figura de ejemplo
        player = "player_mock"
        figure = MagicMock(player=player)
        
        # Prueba caso cuando el jugador ya tiene una carta bloqueada
        mock_has_blocked_figures.return_value = True

        db=MagicMock()
        instance = FigureService(db)

        with self.assertRaises(Exception) as context:
            instance.block_figure(figure)
        self.assertEqual(str(context.exception), "El jugador ya tiene una carta bloqueada")
        

        # Prueba caso cuando el jugador tiene menos de dos cartas
        mock_has_blocked_figures.return_value = False
        mock_get_figures_hand.return_value = ["figura1"]  # Solo una carta en mano
        with self.assertRaises(Exception) as context:
            instance.block_figure(figure)
        self.assertEqual(str(context.exception), "El jugador debe tener mas de dos cartas para ser bloqueado")
        
        # Prueba caso exitoso
        mock_get_figures_hand.return_value = ["figura1", "figura2", "figura3"]  # Tres cartas en mano
        instance.block_figure(figure)
        mock_block_figure_status.assert_called_once_with(db, figure)
        
