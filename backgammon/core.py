from typing import NamedTuple
from numpy.typing import NDArray
from enum import IntEnum
import numpy as np


class Color(IntEnum):

    BLACK = -1
    NONE = 0
    WHITE = +1

    def other(self) -> 'Color':
        return Color(-self)


_COLOR_SYMBOLS = ('X', ' ', 'O')

_START_POINTS = np.array([0, -2, 0, 0, 0, 0, 5, 0, 3, 0, 0, 0,-5, 5, 0, 0, 0,-3, 0,-5, 0, 0, 0, 0, 2, 0])  # noqa: E231
_WHITE_BAR = 25
_BLACK_BAR = 0


def roll_dice(n: int = 2) -> NDArray[np.int_]:
    """Roll `n` dice and return a numpy array of what was rolled."""
    return np.random.randint(1, 7, size=n)


class WinType(IntEnum):
    NORMAL = 1
    GAMMON = 2
    BACKGAMMON = 3


class GameResult(NamedTuple):

    winner: Color = Color.NONE
    doubling_cube: int = 1
    wintype: WinType = WinType.NORMAL

    @property
    def stake(self) -> int:
        return self.wintype * self.doubling_cube


class IllegalMoveError(Exception):
    """Base class for illegal move exceptions."""
    pass


class ImpossibleMoveError(IllegalMoveError):
    """Move that are not only illegal, but also impossible."""
    pass
