from typing import NamedTuple
from enum import Enum
import numpy as np


class Color(Enum):

    BLACK = -1
    NONE = 0
    WHITE = +1

    def other(self) -> 'Color':
        return Color(-self.value)


_COLOR_SYMBOLS = ('X', ' ', 'O')

_START_POINTS = np.array([0, -2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0,-5, 5, 0, 0, 0,-3, 0,-5, 0, 0, 0, 0, 2, 0])  # noqa: E231
_WHITE_BAR = 25
_BLACK_BAR = 0


class GameResult(NamedTuple):
    winner: Color
    doubling_cube: int
    # TODO: this data structure allows for gammon=False and backgammon=True, which does not make sense..
    gammon: bool
    backgammon: bool

    @property
    def stake(self) -> int:
        stake = self.doubling_cube
        if self.backgammon:
            return 3 * stake
        if self.gammon:
            return 2 * stake
        return stake


class IllegalMoveError(Exception):
    """Base class for illegal move exceptions."""
    pass


class ImpossibleMoveError(IllegalMoveError):
    """Move that are not only illegal, but also impossible."""
    pass
