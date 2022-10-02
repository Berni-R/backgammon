from numpy.typing import ArrayLike
import numpy as np

from ..board import Board
from .base import Player
from ..legal import Action, legal_actions


class RandomPlayer(Player):

    def __init__(self, double_prob: float = 0.0, double_take_prob: float = 0.5):
        self.double_prob = double_prob
        self.double_take_prob = double_take_prob

    def choose_action(self, board: Board, dice: ArrayLike) -> Action:
        dice = Player._assert_dice_type(dice)
        actions = legal_actions(board, dice)
        action = actions[np.random.randint(len(actions))]
        return action
