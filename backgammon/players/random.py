from numpy.typing import ArrayLike
import numpy as np

from ..core import Color
from ..board import Board
from .base import Player
from ..legal_actions import Action, legal_actions


class RandomPlayer(Player):

    def __init__(self, double_prob: float = 0.01, double_take_prob: float = 0.8):
        self.double_prob = double_prob
        self.double_take_prob = double_take_prob

    def choose_action(self, board: Board, dice: ArrayLike) -> Action:
        dice = Player._assert_dice_type(dice)
        if board.doubling_turn is Color.NONE or board.turn == board.doubling_turn:
            if np.random.rand() <= self.double_prob:
                return Action([], board.stake * 2)
        actions = legal_actions(board, dice)
        action = actions[np.random.randint(len(actions))]
        return action

    def will_take_doubling(self, board: Board) -> bool:
        return np.random.rand() <= self.double_take_prob
