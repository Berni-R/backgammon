import random
import numpy as np

from backgammon.core.defs import Color, WinType
from backgammon.core.board import Board


def rand_color(allow_none: bool = False) -> Color:
    return Color(random.randint(-1, 1)) if allow_none else Color(2 * random.randint(0, 1) - 1)


def rand_board(allow_none_turn: bool = True) -> Board:
    stake_pow = random.randint(0, 6)
    board = Board(
        np.zeros(26),
        turn=rand_color(allow_none_turn),
        stake_pow=stake_pow,
        doubling_turn=rand_color(stake_pow == 0),
    )
    n_checkers = np.random.randint(1, 15+1, size=2)
    for i in range(np.max(n_checkers)):
        for color in [Color.BLACK, Color.WHITE]:
            if n_checkers[(color + 1) // 2] < i:
                continue
            pnt = np.random.randint(26)
            while board.color_at(pnt) == color.other() or pnt == {Color.BLACK: 25, Color.WHITE: 0}[color]:
                pnt = np.random.randint(26)
            board.points[pnt] += color.value
    return board


BOARDS = [
    Board(),
    Board(
        points=[-6, 0, 1, -1, 2, 0, 0, 0, 0, -7, 0, 0, 1, 0, 0, 0, 0, -1, 0, 8, 0, 0, 0, 0, 0, 1],
        turn=Color.BLACK,
        stake_pow=2,
        doubling_turn=Color.WHITE,
    ),
    Board(
        points=[-1, 0, 1, -2, 4, 0, 1, 0, 0, -7, 0, 0, 1, 0, 0, 3, 0, -5, 0, 0, 0, 0, 0, 0, 0, 3],
        turn=Color.BLACK,
        stake_pow=3,
        doubling_turn=Color.BLACK,
    ),
    Board(
        points=[0, 2, -1, 2, 0, -2, 6, -1, 1, 0, 2, 0, -1, 0, 0, 0, 0, 0, -2, -2, -2, 2, 0, -2, -2, 0],
        turn=Color.WHITE,
        stake_pow=1,
        doubling_turn=Color.BLACK,
    ),
    Board(
        points=[0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -1, -5, -6, 0],
        turn=Color.BLACK,
        stake_pow=0,
        doubling_turn=Color.NONE,
    ),
    Board(
        points=[0, 0, 0, 0, -3, -2, 0, 0, -1, -1, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, -2, -3, 0, -2, 0, 0],
        turn=Color.WHITE,
        stake_pow=0,
        doubling_turn=Color.NONE,
    ),
    Board(
        points=[0, 7, 3, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        turn=Color.BLACK,
        stake_pow=0,
        doubling_turn=Color.NONE,
    ),
]
BOARD_PIP_CNSTS = [(167, 167), (292, 199), (221, 156), (136, 114), (27, 6), (174, 0), (0, 60)]
BOARD_CHECKER_CNT = [(15, 15), (15, 13), (15, 13), (15, 15), (14, 6), (15, 0), (0, 15)]
BOARD_BEARING_OFF = [(False, False), (False, False), (False, False), (False, False), (True, True), (False, True),
                     (True, False)]
BOARD_BEARING_OFF_TURN = [None, False, False, False, True, True, True]
BOARD_CAN_COUBLE = [True, False, True, False, True, True, True]
BOARD_GAME_OVER = [False, False, False, False, False, True, True]
BOARD_WINNERS = [Color.NONE, Color.NONE, Color.NONE, Color.NONE, Color.NONE, Color.WHITE, Color.BLACK]
BOARD_WINTYPES = [
    (WinType.BACKGAMMON, WinType.NORMAL, WinType.BACKGAMMON),
    (WinType.BACKGAMMON, WinType.NORMAL, WinType.NORMAL),
    (WinType.BACKGAMMON, WinType.NORMAL, WinType.NORMAL),
    (WinType.BACKGAMMON, WinType.NORMAL, WinType.BACKGAMMON),
    (WinType.NORMAL, WinType.NORMAL, WinType.NORMAL),
    (WinType.BACKGAMMON, WinType.NORMAL, WinType.NORMAL),
    (WinType.NORMAL, WinType.NORMAL, WinType.GAMMON),
]
BOARD_REPRS = [
    (
        """Board(\n"""
        """  points        = [ 0,-2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0,-5, 5, 0, 0, 0,-3, 0,-5, 0, 0, 0, 0, 2, 0],\n"""
        """  turn          = Color.NONE,\n"""
        """  stake_pow     = 0,\n"""
        """  doubling_turn = Color.NONE,\n"""
        """)"""
    ),
    (
        """Board(\n"""
        """  points        = [-6, 0, 1,-1, 2, 0, 0, 0, 0,-7, 0, 0, 1, 0, 0, 0, 0,-1, 0, 8, 0, 0, 0, 0, 0, 1],\n"""
        """  turn          = Color.BLACK,\n"""
        """  stake_pow     = 2,\n"""
        """  doubling_turn = Color.WHITE,\n"""
        """)"""
    ),
    (
        """Board(\n"""
        """  points        = [-1, 0, 1,-2, 4, 0, 1, 0, 0,-7, 0, 0, 1, 0, 0, 3, 0,-5, 0, 0, 0, 0, 0, 0, 0, 3],\n"""
        """  turn          = Color.BLACK,\n"""
        """  stake_pow     = 3,\n"""
        """  doubling_turn = Color.BLACK,\n"""
        """)"""
    ),
    (
        """Board(\n"""
        """  points        = [ 0, 2,-1, 2, 0,-2, 6,-1, 1, 0, 2, 0,-1, 0, 0, 0, 0, 0,-2,-2,-2, 2, 0,-2,-2, 0],\n"""
        """  turn          = Color.WHITE,\n"""
        """  stake_pow     = 1,\n"""
        """  doubling_turn = Color.BLACK,\n"""
        """)"""
    )
]
BOARD_ASCIIS = [
    (
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
    ),
    (
        """ +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"""
        """ |              X     |   |  O                 |\n"""
        """ |                    |   |  O                 |\n"""
        """ |                    |   |  O                 |\n"""
        """ |                    |   |  O                 |\n"""
        """ |                    | O |  4                 |\n"""
        """^|                    |   |                    |\n"""
        """ |           3        | X |                    |\n"""
        """ |           X        | X |                    |\n"""
        """ |           X        | X |                    |\n"""
        """ |           X        | X |        O           |\n"""
        """ |  O        X        | 2 |        O  X  O     | x 4\n"""
        """ +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"""
        """\n"""
        """Black:  292 pips  /  borne off:  0\n"""
        """White:  199 pips  /  borne off:  2"""
    ),
    (
        """ +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"""
        """ |        O     X     |   |                    | x 8\n"""
        """ |        O     X     |   |                    |\n"""
        """ |        O     X     | O |                    |\n"""
        """ |              X     | O |                    |\n"""
        """ |              X     | O |                    |\n"""
        """^|                    |   |                    |\n"""
        """ |           3        | X |                    |\n"""
        """ |           X        |   |        O           |\n"""
        """ |           X        |   |        O           |\n"""
        """ |           X        |   |        O  X        |\n"""
        """ |  O        X        |   |  O     O  X  O     |\n"""
        """ +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"""
        """\n"""
        """Black:  221 pips  /  borne off:  0\n"""
        """White:  156 pips  /  borne off:  2"""
    ),
    (
        """ +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"""
        """ |                 X  |   |  X  X  O     X  X  | x 2\n"""
        """ |                 X  |   |  X  X  O     X  X  |\n"""
        """ |                    |   |                    |\n"""
        """ |                    |   |                    |\n"""
        """ |                    |   |                    |\n"""
        """v|                    |   |                    |\n"""
        """ |                    |   |  2                 |\n"""
        """ |                    |   |  O                 |\n"""
        """ |                    |   |  O                 |\n"""
        """ |        O           |   |  O  X     O     O  |\n"""
        """ |  X     O     O  X  |   |  O  X     O  X  O  |\n"""
        """ +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"""
        """\n"""
        """Black:  136 pips  /  borne off:  0\n"""
        """White:  114 pips  /  borne off:  0"""
    ),
]
