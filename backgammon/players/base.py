from abc import ABC, abstractmethod
from numpy.typing import ArrayLike, NDArray
import numpy as np

from ..core import Color
from ..board import Board
from ..legal_actions import Action
from ..rating import FIBSRating


class Player(ABC):

    def __init__(self, rating: FIBSRating | float | int):
        self.rating = FIBSRating(rating) if isinstance(rating, float | int) else rating

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

        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @staticmethod
    def _to_nparr_2int(dice: ArrayLike) -> NDArray[np.int_]:
        dice = np.array(dice, dtype=int)
        assert dice.shape == (2,)
        return dice

    @abstractmethod
    def _choose_action(self, board: Board, dice: NDArray[np.int_]) -> Action:
        ...

    @abstractmethod
    def _will_double(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        ...

    @abstractmethod
    def _will_take_doubling(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        ...

    def respond_to_doubling(self, board: Board, points: ArrayLike = (0, 0), match_ends_at: int = 1) -> Action:
        points = self._to_nparr_2int(points)
        # make sure, that `takes` is an actual `bool` and not `np.bool_`
        return Action([], board.stake * 2, takes=bool(self._will_take_doubling(board, points, match_ends_at)))

    def play(self, board: Board, dice: ArrayLike, points: ArrayLike = (0, 0), match_ends_at: int = 1):
        dice = Player._to_nparr_2int(dice)
        points = Player._to_nparr_2int(points)

        if board.doubling_turn is Color.NONE or board.turn == board.doubling_turn:
            if self._will_double(board, points, match_ends_at):
                return Action([], board.stake * 2)

        return self._choose_action(board, dice)
