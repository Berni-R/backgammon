from typing import Sequence
from numpy.typing import NDArray
import numpy as np

from ..core import Color, _COLOR_SYMBOLS, _WHITE_BAR, _BLACK_BAR
from ..board import Board


def board_ascii_art(board: Board, info: bool = True, swap_ints: bool = True,
                    syms: Sequence[str] = _COLOR_SYMBOLS) -> str:
    assert len(syms) == 3
    assert all(isinstance(s, str) for s in syms)
    assert all(len(s) == 1 for s in syms)
    symbols = np.array(syms)

    def build_half(points: NDArray[np.int_], bottom: bool, bar: int):
        points = np.concatenate([points[:6], np.array([bar]), points[6:]])

        rows = []
        for i in range(4):
            signs = np.sign(points)
            rows.append(symbols[signs + 1])
            points -= signs

        def exceed_char(n):
            if n == 0:
                return ' '
            elif abs(n) == 1:
                return symbols[np.sign(n) + 1]
            else:  # more than checker left
                return str(abs(n))

        rows.append(np.fromiter(map(exceed_char, points), dtype='U1'))
        rows_np = np.array(rows)
        rows_np[:, 6] = rows_np[::-1, 6]  # stack checkers on bar from center, not from edge

        if bottom:
            rows_np = rows_np[::-1, ::-1]

        def build_row(row):
            return ' |  ' + '  '.join(row[:6]) + f'  | {row[6]} |  ' + '  '.join(row[7:]) + '  |'

        rows = [build_row(row) for row in rows_np]

        return '\n'.join(rows)

    if swap_ints and board.turn == Color.BLACK:
        s = " +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"
    else:
        s = " +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"
    s += build_half(board.points[13:25], False, board.points[_WHITE_BAR])
    s += "\n |                    |   |                    |\n"
    s += build_half(board.points[1:13], True, board.points[_BLACK_BAR])
    if swap_ints and board.turn == Color.BLACK:
        s += "\n +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"
    else:
        s += "\n +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"

    assert len(s) == 13 * 49
    s_l = list(s)
    s_l[49 * 6] = ('^', '?', 'v')[board.turn + 1]
    s = ''.join(s_l)

    s_l = s.splitlines()
    if board.stake_pow != 0:
        if board.doubling_turn == Color.BLACK:
            s_l[1] += f" x{board.stake:2d}"
        if board.doubling_turn == Color.WHITE:
            s_l[-2] += f" x{board.stake:2d}"
    s = '\n'.join(s_l)

    if info:
        s += '\n'
        for color, name in [(Color.BLACK, "Black"), (Color.WHITE, "White")]:
            s += f"\n{name}:  {board.pip_count(color):3d} pips  /  borne off: {15 - board.checkers_count(color):2d}"

    return s


def print_board(board: Board, info: bool = True, swap_ints: bool = True, syms: Sequence[str] = _COLOR_SYMBOLS,
                **kwargs):
    print(board_ascii_art(board, info=info, swap_ints=swap_ints, syms=syms), **kwargs)
