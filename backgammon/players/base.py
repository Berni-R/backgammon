from abc import ABC, abstractmethod
from numpy.typing import ArrayLike
import numpy as np

from ..board import Board
from ..legal import Action


class Player(ABC):

    @staticmethod
    def _assert_dice_type(dice: ArrayLike) -> np.ndarray:
        dice = np.array(dice, dtype=int)
        assert dice.shape == (2,)
        return dice

    @abstractmethod
    def choose_action(self, board: Board, dice: ArrayLike) -> Action:
        ...

    @abstractmethod
    def will_take_doubling(self, board: Board) -> bool:
        ...

    def respond_to_doubling(self, board: Board) -> Action:
        takes = self.will_take_doubling(board)
        return Action([], board.stake * 2, takes=takes)
