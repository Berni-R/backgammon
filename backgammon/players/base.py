from abc import ABC, abstractmethod
from numpy.typing import ArrayLike, NDArray
import numpy as np

from ..core import Color
from ..board import Board
from ..actions import Doubling, Action


class Player(ABC):

    def __init__(self):
        pass

    @property
    def class_name(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        import inspect

        try:
            attrs = []
            signature = inspect.signature(self.__init__)  # type: ignore
            for arg, p in signature.parameters.items():
                val = getattr(self, arg) if hasattr(self, arg) else getattr(self, '_' + arg)
                if val != p.default:
                    attrs.append(f'{arg}={val}')
        except AttributeError:
            attrs = ["..."]

        return f"{self.class_name}({', '.join(attrs)})"

    @staticmethod
    def _to_nparr_2int(dice: ArrayLike) -> NDArray[np.int_]:
        dice = np.array(dice, dtype=int)
        assert dice.shape == (2,)
        return dice

    @abstractmethod
    def choose_action(self, board: Board, dice: NDArray[np.int_]) -> Action:
        ...

    @abstractmethod
    def will_double(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        ...

    @abstractmethod
    def will_take_doubling(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        ...

    def respond_to_doubling(self, board: Board, points: ArrayLike = (0, 0), match_ends_at: int = 1) -> Action:
        points = self._to_nparr_2int(points)
        if self.will_take_doubling(board, points, match_ends_at):
            doubling = Doubling.TAKE
        else:
            doubling = Doubling.DROP
        return Action([], doubling)

    def play(self, board: Board, dice: ArrayLike, points: ArrayLike = (0, 0), match_ends_at: int = 1,
             no_doubling: bool = False):
        dice = Player._to_nparr_2int(dice)
        points = Player._to_nparr_2int(points)

        if not no_doubling and (board.doubling_turn is Color.NONE or board.turn == board.doubling_turn):
            if self.will_double(board, points, match_ends_at):
                return Action([], Doubling.DOUBLE)

        return self.choose_action(board, dice)
