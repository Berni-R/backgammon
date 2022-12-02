from typing import Any, overload
from numpy.typing import ArrayLike, NDArray
import numpy as np

from .defs import Color, WinType
from .move import Move


START_POINTS = np.array([0, -2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0, -5, 5, 0, 0, 0, -3, 0, -5, 0, 0, 0, 0, 2, 0], dtype=int)
WHITE_BAR = 25
BLACK_BAR = 0


class Board:
    __slots__ = ('points',)

    def __init__(self, points: ArrayLike | None = None, copy: bool = True):
        self.points = START_POINTS.copy() if points is None else np.array(points, dtype=int, copy=copy)
        if self.points.shape != (24 + 2,):
            raise ValueError(f"points must have shape (26,), but got shape {self.points.shape}")

    def __hash__(self) -> int:
        return hash(self.points.tobytes())

    def __repr__(self) -> str:
        def arr2str(arr):
            return "[" + ",".join(map(lambda n: f"{n:2d}", arr)) + "]"
        return f"{self.__class__.__name__}({arr2str(self.points)})"

    def __str__(self) -> str:
        from ..display.board_ascii import board_ascii_art
        return board_ascii_art(self, info=True, swap_ints=False)

    def _repr_svg_(self) -> str:
        from ..display import svg_board
        return svg_board(self).tostring()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Board) and bool(np.all(self.points == other.points))

    def copy(self) -> 'Board':
        return self.__copy__()

    def __copy__(self) -> 'Board':
        return Board(points=self.points, copy=True)

    def flip(self):
        self.points = -self.points[::-1]

    def flipped(self) -> 'Board':
        copy = self.__copy__()
        copy.flip()
        return copy

    def color_at(self, point: int) -> Color:
        return Color(np.sign(self.points[point]))

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

    def checkers_before(self, point: int, color: Color) -> bool:
        if color == Color.WHITE:
            return bool(np.any(self.points[point + 1:] > 0))
        elif color == Color.BLACK:
            return bool(np.any(self.points[:point] < 0))
        else:
            return False

    def bearing_off_allowed(self, color: Color) -> bool:
        if color == Color.WHITE:
            return not self.checkers_before(6, Color.WHITE)
        if color == Color.BLACK:
            return not self.checkers_before(19, Color.BLACK)
        else:  # color == Color.NONE
            raise ValueError("need color to be WHITE or BLACK")

    def do_move(self, move: Move):
        color = np.sign(self.points[move.src])

        if move.hit:
            self.points[move.dst] += color
            self.points[WHITE_BAR if color == Color.BLACK.value else BLACK_BAR] -= color

        self.points[move.src] -= color
        if move.dst not in (BLACK_BAR, WHITE_BAR):
            self.points[move.dst] += color

    def undo_move(self, move: Move):
        if move.dst == BLACK_BAR:
            color = Color.WHITE.value
        elif move.dst == WHITE_BAR:
            color = Color.BLACK.value
        else:
            color = np.sign(self.points[move.dst])

        self.points[move.src] += color
        if move.dst not in (BLACK_BAR, WHITE_BAR):
            self.points[move.dst] -= color

        if move.hit:
            self.points[move.dst] -= color
            self.points[WHITE_BAR if color == Color.BLACK.value else BLACK_BAR] += color
