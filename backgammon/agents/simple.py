from typing import Iterable
from functools import lru_cache
import numpy as np

from ..core import Color, Move, Board, BLACK_BAR, WHITE_BAR
from ..game import Agent, GameState, hit_prob


class SimpleAgent(Agent):
    """A player that plays by simple handwritten rules, but already quite reasonable.

    A strong impact on performance will be from `eval_randomize`. An experiment with match lengths of 1, 3, 5, 7 lead to
    the following relative Glicko-2 ratings (rating devations are between 60 and 65):

        player               | up to 1 |   3  |   5  |  7 points
       ----------------------|---------|------|------|-----------
        eval_randomize = 0   |   2000  | 2000 | 2000 |    2000
        eval_randomize = 1   |   1962  | 1881 | 1937 |    1667
        eval_randomize = 2   |   1936  | 1768 | 1800 |    1663
        eval_randomize = 3   |   1829  | 1732 | 1676 |    1643
        eval_randomize = 4   |   1736  | 1613 | 1635 |    1548
        eval_randomize = 5   |   1597  | 1604 | 1482 |    1443
        eval_randomize = 7   |   1617  | 1435 | 1340 |    1244
        eval_randomize = 8   |   1572  | 1416 | 1254 |    1231
        eval_randomize = 13  |   1415  | 1105 | 1078 |    1037
        eval_randomize = 17  |   1320  | 1132 |  971 |     919
        eval_randomize = 22  |   1199  |  915 |  867 |     789
        eval_randomize = 38  |    982  |  829 |  665 |     700
        eval_randomize = 65  |    913  |  713 |  481 |     420
        eval_randomize = 110 |    870  |  533 |  459 |     317
        eval_randomize = 186 |    842  |  637 |  442 |     259
        eval_randomize = 315 |    754  |  558 |  317 |     263
        RandomAgent()        |    727  |  430 |  274 |     159

    Note the roughly log-linear decrease in rating with `eval_randomize`.
    Furthermore, this descrese itself seems to scale with roughly n^(1/4), where n is the match length. So, in our case
    this is not the n^(1/2) that the FIBS rating system employs. (We do not simply have n games to win, but doubling
    strategies play an important role, too.)
    A fit to empirical data yields the rating estimate (2098+-16) - (184+-6) * n^(0.23+-0.02) * log2(eval_randomize),
    as long as eval_randomize >= 2 / the estiamte is < 2000.
    The above table also implies that the (default) RandomPlayer is about 1300 rating points weaker than the (default)
    SimplePlayer for a single points match (and even more for longer matches).

    Args:
        doubling_th (float):        Player will double the stake, if they judge the winning probability to be higher
                                    than this number. Conversely, accept a doubling if the winnings probability is
                                    judged to be 1 - <doubling_th>.
        eval_randomize (float):     Make the player play more random game.
                                    Adds a normallay distributed variable with the given standard deviation to the move
                                    evaluation. This will reduce (except for very small numbers) the player's strength.
                                    Emperically, it's playing strength will reduce as follows:
        win_prob_randomize (float): Make doubling and taking doubles random.
                                    Like `eval_randomize` this adds a normal random variable to the winning probability
                                    with the given value as standard deviation.
        blot_penalty (float):       Weight for the number of blots of own color to penelise the evaluation.
        bear_off_bonus (float):     Weight for the number of born off checkers of own color to improve the evaluation.
    """

    def __init__(
            self,
            doubling_th: float = 0.8,
            eval_randomize: float = 0.0,
            win_prob_randomize: float = 0.0,
            blot_penalty: float = 0.3,
            bear_off_bonus: float = 1.0,
            illegal_hit_weight: float = 0.7,
    ):
        super().__init__()
        self.doubling_th = doubling_th
        self.eval_randomize = eval_randomize
        self.win_prob_randomize = win_prob_randomize
        self.blot_penalty = blot_penalty
        self.bear_off_bonus = bear_off_bonus
        self.illegal_hit_weight = illegal_hit_weight

        self.eval_board = lru_cache(maxsize=128)(self._eval_board)
        self.eval_move = lru_cache(maxsize=128)(self._eval_move)

    def est_win_prob(self, board: Board, viewpoint: Color | None = None) -> float:
        """Estimate the winning probability (based on the pip count and empirical win rates of RandomPlayer)."""
        # this is only based on pip count - actual checker distribution (such as blots) is entirely ignored
        if viewpoint is None:
            viewpoint = board.turn

        pips = board.pip_count().astype(float)

        # this is an empirical fit to the results of two RandomPlayer playing against each other
        pip_max = np.max(pips)
        scale = 0.42 * pip_max
        win_prob_white = (np.tanh((pips[0] - pips[1]) / scale) + 1) / 2

        win_prob = (1 - win_prob_white) if viewpoint == Color.BLACK else win_prob_white
        win_prob = float(win_prob)

        return win_prob

    def _eval_board(self, board: Board, viewpoint: Color | None = None) -> float:
        """Give the board some evaluation from the given viewpoint. Higher is better.

        Heuristics used:
            [x] use the pip count difference:
                * encourages to hit opponent blots, because then their pip count increases
                * encourages not to play such that dice are not used
            [x] make own blot count reduce value:
                * avoids creating (unneccessary blots)
            [x] substract <hitting prob * pip_count> from value:
                * if creating blots, make being hit more unlikely
                * generally avoid blots closer to the home board more than those to the opponent's home board
            [x] checkers borne off increase value:
                * bore off in single run if possible instead of moving within home board (e.g. 2/off better than 5/3)
            [ ] little encourage for 3+ over 2 checkers at points
            [ ] discourage all checkers on single point
        """
        if viewpoint is None:
            viewpoint = board.turn
        if viewpoint == Color.NONE:
            raise ValueError(f"viewpoint has to be either Color.BLACK or Color.WHITE, got {viewpoint}")

        val_tot = 0.0

        # pip count -> avoid not using a die & promote hitting opponent, when possible
        pips = board.pip_count()
        val = viewpoint * (pips[0] - pips[1])
        val_tot += val

        # helper variables
        blots_mask = (board.points == viewpoint)
        blots_at = np.where(blots_mask)[0]
        pips_add_if_hit = (25 - blots_at) if viewpoint is Color.WHITE else blots_at
        opponent = viewpoint.other()

        # hit prob. * pips -> avoid own blots
        val = 0
        for p, pips_add in zip(blots_at, pips_add_if_hit):
            prob = hit_prob(board, p, opponent, only_legal=True)
            val += prob * pips_add
            bar = {Color.BLACK: BLACK_BAR, Color.WHITE: WHITE_BAR}[viewpoint]
            if board.points[bar] != 0:
                val -= (1 - self.illegal_hit_weight) * prob * pips_add
                val += self.illegal_hit_weight * hit_prob(board, p, opponent, only_legal=False) * pips_add
        val_tot -= val

        # generally penalise blots
        val = self.blot_penalty * blots_mask.sum()
        val_tot -= val

        # encourage bearing off
        val = self.bear_off_bonus * (15 - board.checkers_count(viewpoint))
        val_tot += val

        return val_tot

    def _eval_move(self, state: GameState, move: Move, viewpoint: Color | None = None) -> float:
        # viewpoint of current player, not the one after doing the action!
        if viewpoint is None:
            viewpoint = state.board.turn
        if viewpoint == Color.NONE:
            raise ValueError(f"viewpoint has to be either Color.BLACK or Color.WHITE, got {viewpoint}")

        i = state.do_move(move)
        if any(state.dice_unused):
            legal_moves = state.build_legal_moves()
            if len(legal_moves) == 0:
                val = self.eval_board(state.board, viewpoint)
            else:
                # call the cached version (no leading underscore) of this function!
                val = max(self.eval_move(state, m, viewpoint=viewpoint) for m in legal_moves)
        else:
            val = self.eval_board(state.board, viewpoint)
        state.undo_move(move, i)

        return val

    def choose_move(self, state: GameState, eval_randomize: float | None = None) -> Move:
        legal_moves = state.build_legal_moves()
        assert len(legal_moves) > 0, "No game to choose from"

        move_eval = np.fromiter((self.eval_move(state, move, state.board.turn) for move in legal_moves), float)

        if eval_randomize is None:
            eval_randomize = self.eval_randomize
        if eval_randomize:
            move_eval += np.random.normal(scale=eval_randomize, size=move_eval.size)

        best_idx = np.where(move_eval == np.max(move_eval))[0]
        action = legal_moves[np.random.choice(best_idx)]
        return action

    def will_double(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        # TODO: use points and match_ends_at
        win_prob = self.est_win_prob(state.board)
        if self.eval_randomize:
            win_prob += np.random.normal(scale=self.win_prob_randomize)

        return win_prob > self.doubling_th

    def will_take_doubling(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        # TODO: use points and match_ends_at
        win_prob = self.est_win_prob(state.board)
        if self.eval_randomize:
            win_prob += np.random.normal(scale=self.win_prob_randomize)

        return win_prob > 1.0 - self.doubling_th
