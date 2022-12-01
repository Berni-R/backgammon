from enum import IntEnum
from dataclasses import dataclass


class Color(IntEnum):

    BLACK = -1
    NONE = 0
    WHITE = +1

    def other(self) -> 'Color':
        return Color(-self)


class WinType(IntEnum):
    NORMAL = 1
    GAMMON = 2
    BACKGAMMON = 3


@dataclass(slots=True)
class GameResult:

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
