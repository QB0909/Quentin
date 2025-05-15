import unittest
from client_play import (
    generate_all_pieces, winning_lines, is_winning, game_over, utility,
    get_current_player, get_possible_positions, piece_restantes,
    apply_move, compute_best_move
)

class TestQuartoCore(unittest.TestCase):

    def test_generate_all_pieces(self):
        pieces = generate_all_pieces()
        self.assertEqual(len(pieces), 16)
        self.assertIn("BDEC", pieces)

    def test_winning_lines(self):
        lines = winning_lines()
        self.assertEqual(len(lines), 10)
        for line in lines:
            self.assertEqual(len(line), 4)

    def test_is_winning_true(self):
        board = [None] * 16
        for i in [0, 1, 2, 3]:
            board[i] = "BDEC"
        self.assertTrue(is_winning(board))

    def test_is_winning_false(self):
        board = [None] * 16
        board[0] = "BDEC"
        board[1] = "SDEL"
        self.assertFalse(is_winning(board))

    def test_game_over_win(self):
        board = ["BDEC"] * 4 + [None] * 12
        state = {"board": board}
        self.assertTrue(game_over(state))

    def test_game_over_full(self):
        board = generate_all_pieces()
        state = {"board": board}
        self.assertTrue(game_over(state))

    def test_utility_win(self):
        state = {
            "board": ["BDEC"] * 4 + [None] * 12,
            "current": 0
        }
        self.assertEqual(utility(state, 0), 1)
        self.assertEqual(utility(state, 1), -1)

    def test_get_current_player(self):
        state = {"current": 1}
        self.assertEqual(get_current_player(state), 1)

    def test_get_possible_positions(self):
        board = ["BDEC", None, "SDEL", None]
        board += [None] * 12
        positions = get_possible_positions(board)
        self.assertIn(1, positions)
        self.assertIn(3, positions)
        self.assertEqual(len(positions), 14)

    def piece_restantes(self):
        board = ["BDEC", "SDEL"] + [None] * 14
        current_piece = "BDEL"
        remaining = piece_restantes(board, current_piece)
        self.assertNotIn("BDEC", remaining)
        self.assertNotIn("SDEL", remaining)
        self.assertNotIn("BDEL", remaining)
        self.assertEqual(len(remaining), 13)

    def test_apply_move(self):
        state = {
            "players": ["A", "B"],
            "current": 0,
            "board": [None] * 16,
            "piece": "BDEC"
        }
        new_state = apply_move(state, 0, "SDEL")
        self.assertEqual(new_state["board"][0], "BDEC")
        self.assertEqual(new_state["current"], 1)
        self.assertEqual(new_state["piece"], "SDEL")

    def test_compute_best_move(self):
        board = [None] * 16
        players = ["A", "B"]
        current = "A"
        current_piece = "BDEC"
        pos, piece = compute_best_move(board, players, current, current_piece)
        self.assertIsInstance(pos, int)
        self.assertIsInstance(piece, str)

if __name__ == "__main__":
    unittest.main()
