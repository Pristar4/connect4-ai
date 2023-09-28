from unittest import TestCase

from src.game import Connect4Env, MinMaxPlayer


class TestMinMaxPlayerImproved(TestCase):

    def test_score(self):
        # Create a simple board configuration
        board = Connect4Env()
        player = MinMaxPlayer(8, 10)
        for idx, row in enumerate(board.board):
            # Leave even rows empty and place player 2's pieces on odd rows
            if idx % 2 == 1:
                row[:] = [2] * 7

        # Score should not be 0, as there are connected cells
        score = player.calculate_score(board, 2, 10)
        assert score > 0, f"Expected > 0 but got {score}"

        # Create another board configuration
        board = Connect4Env()
        for idx, row in enumerate(board.board):
            # Leave even rows empty and place player 2's pieces on odd columns
            for col in range(7):
                if col % 2 == 1:
                    row[col] = 2

        # Score should not be 0, as there are connected cells
        score = player.calculate_score(board, 2, 10)
        assert score > 0, f"Expected > 0 but got {score}"

        # Create another board configuration, with no connected cells
        board = Connect4Env()
        for idx, row in enumerate(board.board):
            if idx < 3:
                row[idx] = 2
            else:
                row[idx] = 0

                # Score should be 0, as there are no connected cells
        score = player.calculate_score(board, 2, 10)
        assert score == 0, f"Expected 0 but got {score}"
