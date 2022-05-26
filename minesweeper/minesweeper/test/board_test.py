import unittest
from concurrent.futures import ALL_COMPLETED
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait
from unittest import TestCase, SkipTest
from random import randint
from board import *


class BoardTest(TestCase):

    def test_mines_distribution(self):
        empty, mined = randint(10, 100), randint(10, 100)
        distribution = Board._random_mines_distribution(empty, mined)

        self.assertEqual(
            len([i for i in distribution if not i]),
            empty
        )
        self.assertEqual(
            len([i for i in distribution if i]),
            mined
        )

    def test_contains(self):
        b = Board.create_from_difficulty(Board.DIFF_INTERMEDIATE)
        true_evaluations = [(0, 0), (0, b.width() - 1), (b.height() - 1, 0), (b.height() - 1, b.width() - 1),
                            (b.height() // 2, b.width() // 2)]
        false_evaluations = [(0, -1), (0, b.width()), (b.height(), 0), (b.height() - 1, b.width())]

        for i in true_evaluations:
            self.assertEqual(
                True,
                i in b,
            )

        for i in false_evaluations:
            self.assertEqual(
                False,
                i in b
            )

    def test_board_str(self):
        b = Board.create_from_difficulty(Board.DIFF_HARD)

        for s in b:
            if s.has_bomb:
                b.set_state(s.row, s.col, State.DUG)

        self.assertEqual(
            b.mines_count(),
            str(b).count(Square.REPR_BOMB)
        )
        self.assertEqual(
            len(b) - b.mines_count(),
            str(b).count(State.UNTOUCHED.representation)
        )

    def test_board_len(self):
        """
        Tests the length of a Board instance b when counting its number of squares, and when calculating
        diff[0] * diff[1] (namely, diff."height" * diff."width").
        """
        diff = Board.DIFF_INTERMEDIATE
        boards = [Board.create_from_difficulty(diff) for i in range(100)]

        for b in boards:
            self.assertEqual(
                diff[0] * diff[1],
                len(b)
            )

    def test_from_file(self):
        root = "./assets/"
        files = {
            "safe": ["board_6x6.ms", "board_8x8.ms"],
            "unsafe": ["board_invalid_6x6.ms", "board_invalid_6x7.ms", "board_invalid_7x7.ms"]
        }

        for file in files["safe"]:
            self.assertIsInstance(
                Board.create_from_file(root + file),
                Board
            )

        for file in files["unsafe"]:
            self.assertRaises(
                ValueError,
                Board.create_from_file,
                root + file
            )

    def test_thread_safety(self):
        configs = {
            "threads": 35,
            "cycles": 50,
        }
        board = Board.create_from_difficulty(Board.DIFF_HARD)
        executor = ThreadPoolExecutor(configs["threads"])
        futures = list()

        for i in range(configs["threads"]):
            futures.append(
                executor.submit(
                    board.toggle_dug,
                    configs["cycles"]
                )
            )

        wait(futures, None, ALL_COMPLETED)

        state = board.square(0, 0).state

        for s in board:
            self.assertEqual(
                state,
                s.state
            )


class UncheckedBoardTest:

    @staticmethod
    def print_board():
        """
        Utily method to see some console output when debugging the code, as the unittest framework captures it and
        it didn't seem straightforward to me displaying it.
        """
        b = Board.create_from_difficulty(Board.DIFF_HARD)
        b.toggle_dug(3)

        b.set_state(0, 1, State.DUG)
        b.set_state(3, 1, State.DUG)
        b.set_state(0, 2, State.DUG)
        # b.set_state(0, 1, State.DUG)
        # b.set_state(0, 5, State.DUG)
        # b.set_state(6, 0, State.DUG)
        # b.set_state(0, 8, State.DUG)
        # b.set_state(1, 1, State.DUG)
        # b.set_state(7, 2, State.DUG)
        # b.set_state(4, 1, State.DUG)
        # b.set_state(4, 3, State.FLAGGED)
        # b.set_state(4, 5, State.FLAGGED)

        print(b)

    @staticmethod
    def test_create_probability(size):
        board = Board.create_from_probability(size, size)

        for square in filter(lambda x: x.has_bomb, board):
            board.set_state(square.row, square.col, State.DUG)

        print(board)
        print("Found %d bombs in %d squares (%.3f ratio)" % (board.mines_count(), len(board), board.mines_count() / len(board)))


if __name__ == "__main__":
    unittest.main(BoardTest)
    # UncheckedBoardTest().print_board()