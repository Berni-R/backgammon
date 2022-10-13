from typing import Sequence
from numpy.typing import NDArray, ArrayLike
import numpy as np

from .core import Color
from .match import Match
from .rating import FIBSRating
from .players import Player


class Tournament:

    def __init__(self, players: Sequence[Player], rated: bool = True):
        self.players = [player for player in players]
        n = len(self.players)
        self.wins = np.zeros((n,) * 2, dtype=int)
        self.rounds_played = np.zeros(n, dtype=int)
        self.rounds_played_overall = 0
        self.rated = rated

    @staticmethod
    def _diff_matrix(arr: Sequence, dtype: object | None = None) -> NDArray:
        n = len(arr)
        m = np.empty((n, n), dtype=dtype)  # type: ignore
        for i, w1 in enumerate(arr):
            for j, w2 in enumerate(arr):
                m[i, j] = w1 - w2
        return m

    def rating_diff_matrix(self) -> NDArray[np.float_]:
        return self._diff_matrix([p.rating for p in self.players], float)

    def win_prob_matrix(self, match_len: int = 1) -> NDArray[np.float_]:
        rating_diff = self.rating_diff_matrix()
        win_prob = FIBSRating.win_prob_for_diff(rating_diff, match_len=match_len)
        assert isinstance(win_prob, np.ndarray)
        return win_prob.astype(float)

    def generate_pairs_by_matrix(self, matrix: ArrayLike, stddev: float) -> list[list[int]]:
        matrix = np.array(matrix)
        if matrix.shape != (len(self.players),) * 2:
            raise ValueError(f"matrix must be square of number of players {len(self.players)}, got {matrix.shape}")
        if not np.allclose(np.abs(matrix), np.abs(matrix).T):
            raise ValueError("matrix must be symmetric or anti-symmetric")

        match_prob = np.exp(-0.5 * (matrix / stddev) ** 2)
        n = len(match_prob)
        paired = np.zeros(n, dtype=bool)
        indices = np.arange(n)
        indices_shuffeled = indices.copy()
        np.random.shuffle(indices_shuffeled)
        pairs = []
        for i in indices_shuffeled:
            if paired[i]:
                continue
            paired[i] = True
            if np.sum(~paired):
                p = match_prob[i][~paired]
                partner = np.random.choice(indices[~paired], p=p / p.sum())
                paired[partner] = True
                pairs.append([i, partner])
        return pairs

    def generate_pairs_by_rating(self, rating_stddev: float = 200.0) -> list[list[int]]:
        rating_diffs = self.rating_diff_matrix()
        return self.generate_pairs_by_matrix(rating_diffs, rating_stddev)

    def play_round(self, match_len: int, pairings: list[list[int]] | None = None):
        if pairings is None:
            pairings = self.generate_pairs_by_rating()

        for pair in pairings:
            white = self.players[pair[0]]
            black = self.players[pair[1]]

            match = Match(black=black, white=white, n_points=match_len, rated=self.rated)
            match.play(tqdm_args=dict(disable=True))

            if match.get_winner() is Color.WHITE:
                self.wins[pair[0], pair[1]] += 1
            else:
                self.wins[pair[1], pair[0]] += 1

            self.rounds_played[pair[0]] += 1
            self.rounds_played[pair[1]] += 1

        self.rounds_played_overall += 1
