from typing import Sequence, Optional, Any, overload
from numpy.typing import ArrayLike, NDArray
from math import log2
import numpy as np

from .core import Color, WinType, _COLOR_SYMBOLS, _START_POINTS, GameResult, _WHITE_BAR, _BLACK_BAR
from .moves.move import Move


class Board:

    def __init__(
            self,
            points: Optional[ArrayLike] = None,
            turn: Color = Color.NONE,
            stake_pow: int = 0,
            doubling_turn: Color = Color.NONE,
            copy: bool = True,
    ):
        self.points = _START_POINTS.copy() if points is None else np.array(points, dtype=int, copy=copy)
        if self.points.shape != (24 + 2,):
            raise ValueError(f"points must have shape (26,), but got shape {self.points.shape}")
        self.turn = turn
        self.stake_pow = stake_pow
        self.doubling_turn = doubling_turn

    def __hash__(self) -> int:
        # the int cast makes PyCharm happy...
        return hash(tuple(self.points) + (int(self.turn), self.stake_pow, int(self.doubling_turn)))

    def __repr__(self) -> str:
        def arr2str(arr):
            return "[" + ",".join(map(lambda n: f"{n:2d}", arr)) + "]"
        r = f"Board(\n" \
            f"  points        = {arr2str(self.points)},\n" \
            f"  turn          = {str(self.turn)},\n" \
            f"  stake_pow     = {self.stake_pow},\n" \
            f"  doubling_turn = {str(self.doubling_turn)},\n" \
            f")"
        return r

    def __str__(self) -> str:
        return self.ascii_art(info=False, swap_ints=False)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Board) and (
                bool(np.all(self.points == other.points))
                and self.turn == other.turn
                and self.stake_pow == other.stake_pow
                and self.doubling_turn == other.doubling_turn
        )

    def copy(self) -> 'Board':
        return self.__copy__()

    def __copy__(self) -> 'Board':
        return Board(
            points=self.points,
            turn=self.turn,
            stake_pow=self.stake_pow,
            doubling_turn=self.doubling_turn,
            copy=True,
        )

    def flip(self):
        self.points = -self.points[::-1]
        self.turn = self.turn.other()
        # self.stake_pow = self.stake_pow
        self.doubling_turn = self.doubling_turn.other()

    def flipped(self) -> 'Board':
        copy = self.__copy__()
        copy.flip()
        return copy

    # TODO: type hints for slices and Co.
    def __getitem__(self, point: int) -> int:
        return self.points[point]

    # TODO: type hints for slices and Co.
    def __setitem__(self, point: int, checkers: int):
        self.points[point] = checkers

    def color_at(self, point: int) -> Color:
        return Color(np.sign(self.points[point]))

    def switch_turn(self):
        self.turn = self.turn.other()

    def switch_doubling_turn(self):
        self.doubling_turn = self.doubling_turn.other()

    @property
    def stake(self) -> int:
        return 2 ** self.stake_pow

    @stake.setter
    def stake(self, stake: int):
        stake_pow = int(log2(stake))
        if 2 ** stake_pow != stake:
            raise ValueError(f"stake needs to be a power of 2, got {stake}")
        self.stake_pow = stake_pow

    @overload
    def pip_count(self, color: None = None) -> NDArray[np.int_]: ...

    @overload
    def pip_count(self, color: Color) -> int: ...

    def pip_count(self, color=None):
        if color is None:
            black = (self.points < 0)
            return np.array([
                -np.sum((self.points * np.arange(26)[::-1])[black]),
                np.sum((self.points * np.arange(26))[~black]),
            ])
        else:
            mask = (color * self.points > 0)
            return color * np.sum((self.points * np.arange(26)[::color])[mask])

    @overload
    def checkers_count(self, color: None = None) -> NDArray[np.int_]: ...

    @overload
    def checkers_count(self, color: Color) -> int: ...

    def checkers_count(self, color=None):
        if color is None:
            return np.array([
                -self.points[self.points < 0].sum(),
                self.points[self.points > 0].sum(),
            ])
        else:
            return color * np.sum(self.points[color * self.points > 0])

    def game_over(self) -> bool:
        return bool(np.any(self.pip_count() == 0))

    def winner(self) -> Color:
        pip_cnt = self.pip_count()
        if pip_cnt[0] == 0 and pip_cnt[1] > 0:
            return Color.BLACK
        if pip_cnt[1] == 0 and pip_cnt[0] > 0:
            return Color.WHITE
        else:
            return Color.NONE

    def win_type(self, looser: Color) -> WinType:
        if looser is Color.NONE:
            return WinType.NORMAL
        if self.checkers_count(looser) < 15:
            return WinType.NORMAL
        if (
                (looser == Color.BLACK and self.checkers_before(7, Color.BLACK)) or
                (looser == Color.WHITE and self.checkers_before(18, Color.WHITE))
        ):
            return WinType.BACKGAMMON
        return WinType.GAMMON

    def result(self) -> GameResult:
        winner = self.winner()
        wintype = self.win_type(winner.other())
        return GameResult(winner, self.stake, wintype)

    def checkers_before(self, point: int, color: Color) -> bool:
        if color == Color.WHITE:
            return bool(np.any(self.points[point + 1:] > 0))
        elif color == Color.BLACK:
            return bool(np.any(self.points[:point] < 0))
        else:
            return False

    def bearing_off_allowed(self, color: Optional[Color] = None) -> bool:
        if color is None:
            color = self.turn

        if color == Color.WHITE:
            return not self.checkers_before(6, Color.WHITE)
        if color == Color.BLACK:
            return not self.checkers_before(19, Color.BLACK)
        else:  # color == Color.NONE
            raise ValueError("need color to be WHITE or BLACK")

    def hit_prob(self, point: int, by: Optional[Color] = None, only_legal: bool = False) -> float:
        """Calculate the probability by which the given point can be hit in the next move, given it is legal.

        Args:
            point (int):        The point in question of being hit. This can be any point, also empty ones and those of
                                the same color as `by`.
            by (Color):         By which color the point might be hit. If it is None, it defaults to the opposing color
                                of which the checkers on the given `point` are.
            only_legal (bool):  Restrict to legals moves. This means, that if there are checkers of the hitter's color
                                on the bar, only considers those as potential hitters, ignore all other checkers.

        Returns:
            p (float):          The probabilty by which the given point could be hit in the next move.
        """
        if not 0 <= point <= 25:
            raise IndexError(f"{point} is not a valid point to hit")
        if point in (_BLACK_BAR, _WHITE_BAR):
            return 0.0
        if by is None:
            by = self.color_at(point).other()
        if by is Color.NONE:
            raise ValueError("Color by which to hit is undefined.")
        assert by is not None
        by_i = int(by)

        def is_not_blocked(dist: int) -> bool:
            return 0 <= point + by_i * dist <= 25 and by_i * self.points[point + by_i * dist] >= -1

        if only_legal and by == Color.BLACK and self.points[_BLACK_BAR] < 0:
            hitters_at = np.array([_BLACK_BAR])
        elif only_legal and by == Color.WHITE and self.points[_WHITE_BAR] > 0:
            hitters_at = np.array([_WHITE_BAR])
        else:
            hitters_at = np.where(np.sign(self.points) == by_i)[0]

        dists = by_i * (hitters_at - point)
        options = 0
        for d1 in range(1, 6 + 1):
            if d1 in dists:
                options += 6
                continue
            for d2 in range(1, 6 + 1):
                if d2 in dists:
                    options += 1
                else:
                    if d1 == d2:
                        mid = d1
                        d = 2 * d1
                        while d < 5 * d1:
                            if is_not_blocked(mid):
                                if d in dists:
                                    options += 1
                                    break  # no multi-count of other potential possibilities
                            else:
                                break  # in-between point is blocked - cannot walk further anyway
                            mid += d1
                            d += d1
                    elif d1 + d2 in dists:  # not a double roll
                        if is_not_blocked(d1) or is_not_blocked(d2):
                            options += 1

        return options / 36

    def do_move(self, move: Move):
        color = self.color_at(move.src)

        if move.hit:
            self.points[move.dst] += color
            self.points[_WHITE_BAR if color == Color.BLACK else _BLACK_BAR] -= color

        self.points[move.src] -= color
        if move.dst not in (_BLACK_BAR, _WHITE_BAR):
            self.points[move.dst] += color

    def undo_move(self, move: Move):
        if move.dst == 0:
            color = Color.WHITE
        elif move.dst == 25:
            color = Color.BLACK
        else:
            color = self.color_at(move.dst)

        self.points[move.src] += color
        if move.dst not in (0, 25):
            self.points[move.dst] -= color

        if move.hit:
            self.points[move.dst] -= color
            self.points[_WHITE_BAR if color == Color.BLACK else _BLACK_BAR] += color

    def show(self, info: bool = True, syms: Sequence[str] = _COLOR_SYMBOLS, **kwargs):
        print(self.ascii_art(info=info, syms=syms), **kwargs)

    def ascii_art(self, info: bool = True, swap_ints: bool = True, syms: Sequence[str] = _COLOR_SYMBOLS) -> str:
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

        if swap_ints and self.turn == Color.BLACK:
            s = " +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"
        else:
            s = " +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"
        s += build_half(self.points[13:25], False, self.points[_WHITE_BAR])
        s += "\n |                    |   |                    |\n"
        s += build_half(self.points[1:13], True, self.points[_BLACK_BAR])
        if swap_ints and self.turn == Color.BLACK:
            s += "\n +-13-14-15-16-17-18--+---+-19-20-21-22-23-24--+\n"
        else:
            s += "\n +-12-11-10--9--8--7--+---+--6--5--4--3--2--1--+\n"

        assert len(s) == 13 * 49
        s_l = list(s)
        s_l[49 * 6] = ('^', '?', 'v')[self.turn + 1]
        s = ''.join(s_l)

        s_l = s.splitlines()
        if self.stake_pow != 0:
            if self.doubling_turn == Color.BLACK:
                s_l[1] += f" x{self.stake:2d}"
            if self.doubling_turn == Color.WHITE:
                s_l[-2] += f" x{self.stake:2d}"
        s = '\n'.join(s_l)

        if info:
            s += '\n'
            for color, name in [(Color.BLACK, "Black"), (Color.WHITE, "White")]:
                s += f"\n{name}:  {self.pip_count(color):3d} pips  /  borne off: {15 - self.checkers_count(color):2d}"

        return s
