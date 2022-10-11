from typing import Any, Union
from math import sqrt
from numpy.typing import NDArray
import numpy as np

INITIAL_RATING = 1500.0


class FIBSRating:

    def __init__(self, value: float | int = INITIAL_RATING, experience: int = 0, ramp_up: bool = True,
                 fixed: bool = False):
        self.value = float(value)
        self.experience = experience
        self.ramp_up = ramp_up
        self.fixed = fixed

    def __repr__(self) -> str:
        r = f'FIBSRating({self.value:.1f}, experience={self.experience:,d}, ramp_up={self.ramp_up}, fixed={self.fixed})'
        return r

    def __str__(self) -> str:
        return f'{self.value:.1f}'

    def __float__(self) -> float:
        return float(self.value)

    def __lt__(self, other: Union['FIBSRating', float, int]) -> bool:
        return self.value < float(other)

    def __gt__(self, other: Union['FIBSRating', float, int]) -> bool:
        return self.value > float(other)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, FIBSRating | float | int):
            return self.value == float(other)
        return False

    def win_prob(self, opponent: Union['FIBSRating', float, int], match_len: int) -> float:
        diff = self.value - float(opponent)
        return 1.0 / (1.0 + 10.0 ** (-diff * sqrt(match_len) / 2000.0))

    def ramp_up_mult(self) -> float:
        return max(1.0, 5.0 - self.experience / 100.0) if self.ramp_up else 1.0

    @staticmethod
    def mutual_update(winner: 'FIBSRating', looser: 'FIBSRating', match_len: int) -> NDArray[np.int_]:
        s = 4.0 * sqrt(match_len)
        p = winner.win_prob(looser, match_len)

        d_winner = (1.0 - p) * s * winner.ramp_up_mult()
        d_looser = p * s * winner.ramp_up_mult()

        if not winner.fixed:
            winner.value += d_winner
        if not looser.fixed:
            looser.value -= d_looser

        winner.experience += match_len
        looser.experience += match_len

        return np.array([d_winner, d_looser])
