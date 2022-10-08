import numpy as np

from backgammon.core import Color
from backgammon.board import Board


def test_hit_prob():
    # probabilities on an empty board
    probs_raw = np.array([11, 12, 14, 15, 15, 17,
                          6,  6,  5,  3,  2,  3,  # noqa: E127
                          0,  0,  1,  1,  0,  1,  # noqa: E127
                          0,  1,  0,  0,  0,  1]) / 36  # noqa: E127
    # empty board
    board = Board(points=np.zeros(26))
    board[1] = Color.BLACK  # hit a black checkers at point 1
    probs = []
    for i in range(1, 4 * 6 + 1):
        board[1 + i] = 1
        probs.append(board.hit_prob(1))  # try to hit that black checker on point 1
        board[1 + i] = 0
    assert np.all(probs_raw == probs)

    # simple blocks (with shifted checker to hit)
    board = Board(points=np.zeros(26))
    i = 17
    board[i] = Color.WHITE  # to be hit
    board[i - 4] = 3 * Color.BLACK  # multiple checkers at start
    assert board.hit_prob(i) * 36 == 15
    board[i - 2] = Color.WHITE  # one checker does not block (but can be hit - not asked for, though)
    assert board.hit_prob(i) * 36 == 15
    board[i - 2] = 2 * Color.BLACK  # neither do multiple own checkers, but they actually also can hit
    assert board.hit_prob(i) * 36 == 23  # > 15
    board[i - 2] = 2 * Color.WHITE  # but two opponent checkers do block
    assert board.hit_prob(i) * 36 == 13  # < 15

    board = Board(points=np.zeros(26))
    i = 13
    board[i] = Color.BLACK  # to be hit
    board[i + 6] = Color.WHITE  # hit from
    assert board.hit_prob(i) * 36 == 17
    board[i + 9] = Color.WHITE  # add more sources
    assert board.hit_prob(i) * 36 == 19
    board[i + 7] = 2 * Color.BLACK  # (partial) block, but ineffective
    assert board.hit_prob(i) * 36 == 19
    board[i + 2] = 2 * Color.BLACK  # now useful
    assert board.hit_prob(i) * 36 == 18

    # a complex example
    board = Board(points=[-2, -1, -1, -1, 2, -3, 0, 0, 2, 3, 0, 0, 0, -1, 1, 1, 0, 0, -2, -2, 1, 1, -1, 2, -1, 0])
    w = np.array([0, 21, 26, 33, 25, 26, 25, 25, 29, 29, 26, 26, 26, 27, 27, 26, 24, 29, 29, 27, 20, 12, 11, 0, 0, 0])
    b = np.array([0, 11, 20, 27, 32, 32, 35, 35, 34, 28, 22, 21, 14, 9, 16, 16, 17, 17, 17, 25, 23, 23, 25, 31, 30, 0])
    b_legal = np.array([0, 11, 12, 14, 15, 15, 16, 6, 4, 5, 3, 2, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0])
    c = np.array([0, 21, 26, 33, 32, 26, 0, 0, 34, 28, 0, 0, 0, 27, 16, 16, 0, 0, 29, 27, 23, 23, 11, 31, 0, 0])
    c_legal = np.array([0, 21, 26, 33, 15, 26, 0, 0, 4, 5, 0, 0, 0, 27, 0, 1, 0, 0, 29, 27, 1, 0, 11, 0, 0, 0])
    assert np.all(w == (36 * np.array([board.hit_prob(i, Color.WHITE) for i in range(26)])).astype(int))
    assert np.all(w == (
            36 * np.array([board.hit_prob(i, Color.WHITE, only_legal=True) for i in range(26)])).astype(int))
    assert np.all(b == (36 * np.array([board.hit_prob(i, Color.BLACK) for i in range(26)])).astype(int))
    assert np.all(b_legal == (
            36 * np.array([board.hit_prob(i, Color.BLACK, only_legal=True) for i in range(26)])).astype(int))
    assert np.all(c == (36 * np.array([board.hit_prob(i) if board[i] != 0 else 0 for i in range(26)])).astype(int))
    assert np.all(c_legal == (
            36 * np.array([board.hit_prob(i, only_legal=True) if board[i] != 0 else 0 for i in range(26)])).astype(int))
