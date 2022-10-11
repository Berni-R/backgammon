from numpy.typing import NDArray
import numpy as np

from ..board import Board
from .base import Player
from ..legal_actions import Action, build_legal_actions
from ..rating import FIBSRating, INITIAL_RATING


class RandomPlayer(Player):

    def __init__(self, rating: FIBSRating | float | int = INITIAL_RATING, double_prob: float = 0.005,
                 double_take_prob: float = 0.8):
        super().__init__(rating)
        self.double_prob = double_prob
        self.double_take_prob = double_take_prob

    def _choose_action(self, board: Board, dice: NDArray[np.int_]) -> Action:
        actions = build_legal_actions(board, dice)
        action = actions[np.random.randint(len(actions))]
        return action

    def _will_double(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        return np.random.rand() <= self.double_prob

    def _will_take_doubling(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        return np.random.rand() <= self.double_take_prob
