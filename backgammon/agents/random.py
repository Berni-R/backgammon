from typing import Iterable
import random

from ..core import Move
from ..game import Agent, GameState


class RandomAgent(Agent):

    def __init__(self, double_prob: float = 0.005, double_take_prob: float = 0.8):
        super().__init__()
        self.double_prob = double_prob
        self.double_take_prob = double_take_prob

    def choose_move(self, state: GameState) -> Move:
        legal_moves = state.build_legal_moves()
        assert len(legal_moves) > 0, "No moves to choose from"
        return random.choice(legal_moves)

    def will_double(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        return random.random() <= self.double_prob

    def will_take_doubling(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        return random.random() <= self.double_take_prob
