from typing import Any, overload
from numpy.typing import ArrayLike, NDArray
from math import log2
import numpy as np

from .defs import Color, WinType, GameResult
from .move import Move


START_POINTS = np.array([0, -2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2, 0])
WHITE_BAR = 25
BLACK_BAR = 0


class Board:

    def __init__(
            self,
            points: ArrayLike | None = None,
            turn: Color = Color.NONE,
            stake_pow: int = 0,
            doubling_turn: Color = Color.NONE,
            copy: bool = True,
    ):
        self.points = START_POINTS.copy() if points is None else np.array(points, dtype=int, copy=copy)
        if self.points.shape != (24 + 2,):
            raise ValueError(f"points must have shape (26,), but got shape {self.points.shape}")
        self.turn = turn
        self.stake_pow = stake_pow
        self.doubling_turn = doubling_turn

    def __hash__(self) -> int:
        # the int cast makes PyCharm happy...
        return hash(self.points.tobytes()) ^ hash((int(self.turn), self.stake_pow, int(self.doubling_turn)))

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
        from ..display.board_ascii import board_ascii_art
        return board_ascii_art(self, info=True, swap_ints=False)

    def _repr_svg_(self) -> str:
        from ..display import svg_board
        return svg_board(self).tostring()

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

    def color_at(self, point: int) -> Color:
        return Color(np.sign(self.points[point]))

    def switch_turn(self):
        self.turn = self.turn.other()

    def switch_doubling_turn(self):
        self.doubling_turn = self.doubling_turn.other()

    def can_couble(self) -> bool:
        return self.doubling_turn == Color.NONE or self.doubling_turn == self.turn

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
        return any(self.pip_count() == 0)

    def winner(self) -> Color:
        pip_cnt = self.pip_count()
        if pip_cnt[0] == 0 and pip_cnt[1] > 0:
            return Color.BLACK
        if pip_cnt[1] == 0 and pip_cnt[0] > 0:
            return Color.WHITE
        else:
            return Color.NONE

    def win_type(self, *, looser: Color) -> WinType:
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
        wintype = self.win_type(looser=winner.other())
        return GameResult(winner, self.stake, wintype)

    def checkers_before(self, point: int, color: Color) -> bool:
        if color == Color.WHITE:
            return bool(np.any(self.points[point + 1:] > 0))
        elif color == Color.BLACK:
            return bool(np.any(self.points[:point] < 0))
        else:
            return False

    def bearing_off_allowed(self, color: Color | None = None) -> bool:
        if color is None:
            color = self.turn

        if color == Color.WHITE:
            return not self.checkers_before(6, Color.WHITE)
        if color == Color.BLACK:
            return not self.checkers_before(19, Color.BLACK)
        else:  # color == Color.NONE
            raise ValueError("need color to be WHITE or BLACK")

    def do_move(self, move: Move):
        color = self.color_at(move.src)

        if move.hit:
            self.points[move.dst] += color
            self.points[WHITE_BAR if color == Color.BLACK else BLACK_BAR] -= color

        self.points[move.src] -= color
        if move.dst not in (BLACK_BAR, WHITE_BAR):
            self.points[move.dst] += color

    def undo_move(self, move: Move):
        if move.dst == 0:
            color = Color.WHITE
        elif move.dst == 25:
            color = Color.BLACK
        else:
            color = self.color_at(move.dst)

        self.points[move.src] += color
        if not move.bearing_off():
            self.points[move.dst] -= color

        if move.hit:
            self.points[move.dst] -= color
            self.points[WHITE_BAR if color == Color.BLACK else BLACK_BAR] += color
