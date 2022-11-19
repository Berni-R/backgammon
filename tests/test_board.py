from typing import Optional

import pytest

import numpy as np

from backgammon.core import Color
from backgammon.moves.move import Move
from backgammon.board import Board
from backgammon.display import board_ascii_art


def rand_color(allow_none: bool = False) -> Color:
    return Color(np.random.randint(-1, 2)) if allow_none else Color(2 * np.random.randint(2) - 1)


def rand_board() -> Board:
    board = Board(
        np.zeros(26),
        turn=rand_color(True),
        stake_pow=np.random.randint(0, 7),
        doubling_turn=rand_color(True),
    )
    n_checkers = np.random.randint(1, 15+1, size=2)
    for _ in range(np.max(n_checkers)):
        for color in [Color.BLACK, Color.WHITE]:
            i = np.random.randint(26)
            while board.color_at(i) == color.other() or i == {Color.BLACK: 25, Color.WHITE: 0}[color]:
                i = np.random.randint(26)
            board.points[i] += color.value
    return board


def test_board():
    board = Board()
    assert repr(board) == (
        """Board(\n"""
        """  points        = [ 0,-2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0,-5, 5, 0, 0, 0,-3, 0,-5, 0, 0, 0, 0, 2, 0],\n"""
        """  turn          = Color.NONE,\n"""
        """  stake_pow     = 0,\n"""
        """  doubling_turn = Color.NONE,\n"""
        """)"""
    )
    assert board_ascii_art(board) == (
        """ +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"""
        """ |  O           X     |   |  X              O  |\n"""
        """ |  O           X     |   |  X              O  |\n"""
        """ |  O           X     |   |  X                 |\n"""
        """ |  O                 |   |  X                 |\n"""
        """ |  O                 |   |  X                 |\n"""
        """?|                    |   |                    |\n"""
        """ |  X                 |   |  O                 |\n"""
        """ |  X                 |   |  O                 |\n"""
        """ |  X           O     |   |  O                 |\n"""
        """ |  X           O     |   |  O              X  |\n"""
        """ |  X           O     |   |  O              X  |\n"""
        """ +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"""
        """\n"""
        """Black:  167 pips  /  borne off:  0\n"""
        """White:  167 pips  /  borne off:  0"""
    )

    board = Board(
        points=[-2, 0,1,-2,2,0,0,0,0,-7,0,0,1,0,0,0,0,-4,0,8,0,0,0,0,0, 1],  # noqa: E231
        turn=Color.BLACK,
        stake_pow=3,
        doubling_turn=Color.WHITE,
    )
    assert repr(board) == (
        """Board(\n"""
        """  points        = [-2, 0, 1,-2, 2, 0, 0, 0, 0,-7, 0, 0, 1, 0, 0, 0, 0,-4, 0, 8, 0, 0, 0, 0, 0, 1],\n"""
        """  turn          = Color.BLACK,\n"""
        """  stake_pow     = 3,\n"""
        """  doubling_turn = Color.WHITE,\n"""
        """)"""
    )
    assert all(board.pip_count() == [238, 199])
    assert board.pip_count(Color.BLACK) == 238
    assert board.pip_count(Color.WHITE) == 199
    assert all(board.checkers_count() == [15, 13])
    assert board.checkers_count(Color.BLACK) == 15
    assert board.checkers_count(Color.WHITE) == 13
    assert board_ascii_art(board) == (
        """ +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"""
        """ |              X     |   |  O                 |\n"""
        """ |              X     |   |  O                 |\n"""
        """ |              X     |   |  O                 |\n"""
        """ |              X     |   |  O                 |\n"""
        """ |                    | O |  4                 |\n"""
        """^|                    |   |                    |\n"""
        """ |           3        | X |                    |\n"""
        """ |           X        | X |                    |\n"""
        """ |           X        |   |                    |\n"""
        """ |           X        |   |        O  X        |\n"""
        """ |  O        X        |   |        O  X  O     | x 8\n"""
        """ +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"""
        """\n"""
        """Black:  238 pips  /  borne off:  0\n"""
        """White:  199 pips  /  borne off:  2"""
    )
    for point, color in [(1, Color.NONE), (2, Color.WHITE), (3, Color.BLACK), (19, Color.WHITE), (11, Color.NONE)]:
        assert board.color_at(point) == color

    with pytest.raises(TypeError):
        board.stake = "stake"
    with pytest.raises(ValueError):
        board.stake = -16
    with pytest.raises(ValueError):
        board.stake = 15

    with pytest.raises(ValueError):
        Board(np.zeros((2, 5), dtype=int))


def test_board_hash():
    board = Board(
        points=[1, 0,1,-2,4,0,1,0,0,-7,0,0,1,0,0,6,0,-5,0,8,0,0,0,0,0, 3],  # noqa: E231
        turn=Color.BLACK,
        stake_pow=3,
    )
    assert isinstance(hash(board), int)
    assert hash(board) != hash(Board())

    for _ in range(5):
        board = rand_board()
        hash(board)


def test_board_copy():
    board = Board()
    assert board is not board.copy()
    assert board == board.copy()

    board = Board(
        points=[1, 0,1,-2,4,0,1,0,0,-7,0,0,1,0,0,6,0,-5,0,8,0,0,0,0,0, 3],  # noqa: E231
        turn=Color.BLACK,
        stake_pow=3,
    )
    assert board is not Board()
    assert board != Board()
    assert board is not board.copy()
    assert board == board.copy()


def test_do_undo_moves():
    def check_move(board_: Board, move_: Move, point: Optional[int] = None, val: int = 0):
        b = board_.copy()
        b.do_move(move_)
        assert b != board_
        if point is not None:
            assert b.points[point] == val
        elif move_.dst not in (0, 25):
            assert np.sign(b.points[move_.dst]) == board_.color_at(move_.src)
        b.undo_move(move_)
        assert b == board_

    board = Board()
    for move in [Move(8, 5), Move(12, 17), Move(13, 11)]:
        check_move(board, move)

    board = Board(points=[-2, 0, 0, 1, 1, 1, 1, 1, 0, 0, -2, -1, 3, 0, 0, 2, -1, -3, -2, 1, 1, 0, 0, 0, -1, 1])
    for move in [
            Move(0, 5, hit=True), Move(16, 19, hit=True),  # hitting
            Move(25, 20),  Move(6, 3), Move(10, 16),  # bar -> somewhere
            Move(6, 0), Move(24, 25),  # bear off
    ]:
        check_move(board, move)
    check_move(board, Move(15, 11, hit=True), 15, 1)
    check_move(board, Move(15, 11, hit=True), 11, 1)
    check_move(board, Move(10, 5, hit=True), 10, -1)
    check_move(board, Move(10, 5, hit=True), 5, -1)
    check_move(board, Move(17, 18), 17, -2)
    check_move(board, Move(17, 18), 18, -3)
