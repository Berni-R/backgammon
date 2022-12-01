import pytest
import random
import numpy as np

from backgammon.core.defs import Color
from backgammon.core.move import Move
from backgammon.core.board import Board

from defs import rand_board, BOARDS


def build_random_move(board: Board, color: Color) -> Move:
    if board.checkers_count(color) == 0:
        raise ValueError(f"no checkers for color {color} on board")

    while True:
        points_of_color = np.where(np.sign(board.points) == color)[0]
        src = int(np.random.choice(points_of_color))
        pips = random.randint(1, 6)
        dst = max(0, min(25, src - color * pips))
        hit = (board.color_at(dst) == color.other())
        if not hit or abs(board.points[dst]) == 1:
            return Move(src, dst, hit=hit)


@pytest.mark.parametrize('board', BOARDS + [rand_board(False) for _ in range(20)])
def test_do_undo_random_moves(board: Board):
    for color in [Color.BLACK, Color.WHITE]:
        if board.checkers_count(color) == 0:
            continue
        for _ in range(5):
            move = build_random_move(board, color)

            board_orig = board.copy()
            board.do_move(move)

            # the points, but nothing else should have changed
            assert np.any(board.points != board_orig.points)
            assert board.turn == board_orig.turn
            assert board.stake_pow == board_orig.stake_pow
            assert board.doubling_turn == board_orig.doubling_turn

            if move.bearing_off():
                # only the moved checker was removed form board
                assert board.checkers_count(color) == board_orig.checkers_count(color) - 1
                assert board.checkers_count(color.other()) == board_orig.checkers_count(color.other())
            else:
                # no checkers are lost
                assert np.all(board.checkers_count() == board_orig.checkers_count())
                # have checker(s) at destination of the same color as those that were on source
                assert np.sign(board.points[move.dst]) == board_orig.color_at(move.src)

            # removed a checker from source
            assert abs(board.points[move.src]) == abs(board_orig.points[move.src]) - 1
            # added a checker to destination, if not born off or hit
            if not move.bearing_off():
                if move.hit:
                    assert abs(board.points[move.dst]) == abs(board_orig.points[move.dst])
                else:
                    assert abs(board.points[move.dst]) == abs(board_orig.points[move.dst]) + 1

            # undoing must revert to original state
            board.undo_move(move)
            assert board == board_orig
