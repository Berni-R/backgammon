from typing import Sequence, Optional, overload
from numpy.typing import ArrayLike
import numpy as np

from .core import Color, _COLOR_SYMBOLS, _START_POINTS, GameResult, _WHITE_BAR, _BLACK_BAR
from .move import Move


class Board:

    def __init__(
            self,
            points: Optional[ArrayLike] = None,
            turn: Color = Color.NONE,
            stake_pow: int = 0,
            copy: bool = True,
    ):
        self._points = _START_POINTS.copy() if points is None else np.array(points, dtype=int, copy=copy)
        if self._points.shape != (24 + 2,):
            raise ValueError(f"points must have shape (26,), but got shape {self._points.shape}")
        self._turn = turn
        self._stake_pow = stake_pow

    def __hash__(self) -> int:
        return hash(tuple(self._points) + (self._turn, self._stake_pow))

    def __repr__(self) -> str:
        def arr2str(arr):
            return "[" + ",".join(map(lambda n: f"{n:2d}", arr)) + "]"
        r = f"State(\n" \
            f"  points     = {arr2str(self._points)},\n" \
            f"  turn       = {self._turn},\n" \
            f"  stake_pow  = {self._stake_pow},\n" \
            f")"
        return r

    def __eq__(self, other: 'Board') -> bool:
        return (
                np.all(self._points == other._points)
                and self._turn == other._turn
                and self._stake_pow == other._stake_pow
        )

    def copy(self) -> 'Board':
        return self.__copy__()

    def __copy__(self) -> 'Board':
        return Board(
            points=self._points,
            turn=self._turn,
            stake_pow=self._stake_pow,
            copy=True,
        )

    def flip(self):
        self._points = -self._points[::-1]
        self._turn = self._turn.other()
        # self._stake_pow = self._stake_pow

    def flipped(self, copy: bool = True) -> 'Board':
        return Board(
            points=-self._points[::-1],
            turn=self._turn.other(),
            stake_pow=self._stake_pow,
            copy=copy,
        )

    # TODO: type hints for slices and Co.
    def __getitem__(self, point: int) -> int:
        return self._points[point]

    # TODO: type hints for slices and Co.
    def __setitem__(self, point: int, checkers: int):
        self._points[point] = checkers

    def color_at(self, point: int) -> Color:
        return Color(np.sign(self._points[point]))

    @property
    def turn(self) -> Color:
        return self._turn

    @turn.setter
    def turn(self, turn: Color):
        if not isinstance(turn, Color):
            raise TypeError(f"can only set turn to type Color, got {type(turn)}")
        self._turn = turn

    def switch_turn(self):
        self._turn = self._turn.other()

    @property
    def stake(self) -> int:
        return 2 ** self._stake_pow

    @stake.setter
    def stake(self, stake: int):
        if not isinstance(stake, int):
            raise TypeError(f"can only set stake to type int, got {type(stake)}")
        if stake <= 0:
            raise ValueError(f"stake needs to be positive, got {stake}")
        stake_pow = int(np.log2(stake))
        if 2 ** stake_pow != stake:
            raise ValueError(f"stake needs to be a power of 2, got {stake}")
        self._stake_pow = stake_pow

    def double_stake(self) -> int:
        self._stake_pow += 1
        return 2 ** self._stake_pow

    @overload
    def pip_count(self, color: None = None) -> np.ndarray: ...

    @overload
    def pip_count(self, color: Color) -> int: ...

    def pip_count(self, color=None):
        if color is None:
            black = (self._points < 0)
            return np.array([
                -np.sum((self._points * np.arange(26)[::-1])[black]),
                np.sum((self._points * np.arange(26))[~black]),
            ])
        else:
            mask = (color.value * self._points > 0)
            return color.value * np.sum((self._points * np.arange(26)[::color.value])[mask])

    @overload
    def checkers_count(self, color: None = None) -> np.ndarray: ...

    @overload
    def checkers_count(self, color: Color) -> int: ...

    def checkers_count(self, color=None):
        if color is None:
            return np.array([
                -self._points[self._points < 0].sum(),
                self._points[self._points > 0].sum(),
            ])
        else:
            return color.value * np.sum(self._points[color.value * self._points > 0])

    def game_over(self) -> bool:
        return np.any(self.pip_count() == 0)

    def winner(self) -> Color:
        pip_cnt = self.pip_count()
        if pip_cnt[0] == 0 and pip_cnt[1] > 0:
            return Color.BLACK
        if pip_cnt[1] == 0 and pip_cnt[0] > 0:
            return Color.WHITE
        else:
            return Color.NONE

    def result(self) -> GameResult:
        winner = self.winner()
        gammon, backgammon = False, False
        if winner is not Color.NONE:
            looser = winner.other()
            if self.checkers_count(looser) == 15:
                gammon = True
                if looser == Color.BLACK and self.checkers_before(7, Color.WHITE):
                    backgammon = True
                if looser == Color.WHITE and self.checkers_before(18, Color.WHITE):
                    backgammon = True
        return GameResult(winner, 2 ** self._stake_pow, gammon, backgammon)

    def checkers_before(self, point: int, color: Color) -> bool:
        if color == Color.WHITE:
            return np.any(self._points[point + 1:] > 0)
        elif color == Color.BLACK:
            return np.any(self._points[:point] < 0)
        else:
            return False

    def bearing_off_allowed(self, color: Optional[Color] = None) -> bool:
        if color is None:
            color = self._turn

        if color == Color.WHITE:
            return not self.checkers_before(6, Color.WHITE)
        if color == Color.BLACK:
            return not self.checkers_before(19, Color.BLACK)
        else:  # color == Color.NONE
            raise ValueError("need color to be WHITE or BLACK")

    def do_move(self, move: Move):
        color = self.color_at(move.src)

        if move.hit:
            self._points[move.dst] += color.value
            self._points[_WHITE_BAR if color == Color.BLACK else _BLACK_BAR] -= color.value

        self._points[move.src] -= color.value
        if move.dst not in (_BLACK_BAR, _WHITE_BAR):
            self._points[move.dst] += color.value

    def undo_move(self, move: Move):
        if move.dst == 0:
            color = Color.WHITE
        elif move.dst == 25:
            color = Color.BLACK
        else:
            color = self.color_at(move.dst)

        self._points[move.src] += color.value
        if move.dst not in (0, 25):
            self._points[move.dst] -= color.value

        if move.hit:
            self._points[move.dst] -= color.value
            self._points[_WHITE_BAR if color == Color.BLACK else _BLACK_BAR] += color.value

    def show(self, syms: Sequence[str] = _COLOR_SYMBOLS, **kwargs):
        print(self.ascii_art(syms), **kwargs)

    def ascii_art(self, syms: Sequence[str] = _COLOR_SYMBOLS) -> str:
        assert len(syms) == 3
        assert all(isinstance(s, str) for s in syms)
        assert all(len(s) == 1 for s in syms)
        symbols = np.array(syms)

        def build_half(points: np.ndarray, flip: bool, bar: int):
            points = np.concatenate([points[:6], [bar], points[6:]])

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
            rows = np.array(rows)
            rows[:, 6] = rows[::-1, 6]  # stack checkers on bar from center, not from edge

            if flip:
                rows = rows[::-1, ::-1]

            def build_row(row):
                return ' |  ' + '  '.join(row[:6]) + f'  | {row[6]} |  ' + '  '.join(row[7:]) + '  |'
            rows = '\n'.join([build_row(row) for row in rows])

            return rows

        if self._turn == Color.BLACK:
            s = " +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"
        else:
            s = " +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"
        s += build_half(self._points[13:25], False, self._points[-1])
        s += "\n |                    |"
        s += ("BAR" if self._stake_pow == 0 else f"x{self.stake:2d}" if self.stake < 100 else f"{self.stake:3d}")
        s += "|                    |\n"
        s += build_half(self._points[1:13], True, self._points[0])
        if self._turn == Color.BLACK:
            s += "\n +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"
        else:
            s += "\n +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"

        s = list(s)
        assert len(s) == 13 * 49

        s[49 * 6] = ('^', '?', 'v')[self._turn.value + 1]

        return ''.join(s)
