from typing import Optional
from numpy.typing import NDArray
import numpy as np

from ..core import Color
from ..board import Board
from .base import Player
from ..actions import Action, build_legal_actions, do_action, undo_action


class SimplePlayer(Player):
    """A player that plays by simple handwritten rules, but already quite reasonable.

    A strong impact on performance will be from `eval_randomize`. An experiment with match lengths of 1, 3, 5, 7 lead to
    the following relative Glicko-2 ratings (rating devations are between 60 and 65):

        player               | up to 1 |   3  |   5  |  7 points
       ----------------------|---------|------|------|-----------
        eval_randomize = 0   |   2000  | 2000 | 2000 |    2000
        eval_randomize = 1   |   2031  | 1951 | 1840 |    1795
        eval_randomize = 2   |   1977  | 1940 | 1822 |    1766
        eval_randomize = 4   |   1869  | 1805 | 1664 |    1562
        eval_randomize = 7   |   1769  | 1577 | 1471 |    1400
        eval_randomize = 13  |   1547  | 1394 | 1323 |    1328
        eval_randomize = 22  |   1436  | 1221 | 1156 |    1069
        eval_randomize = 38  |   1289  | 1006 | 1015 |     981
        eval_randomize = 65  |   1256  |  924 |  914 |     803
        eval_randomize = 110 |   1124  |  828 |  766 |     697
        eval_randomize = 186 |   1140  |  773 |  671 |     594
        eval_randomize = 315 |   1136  |  763 |  639 |     585
        RandomPlayer()       |   1053  |  655 |  527 |     498

    Note the roughly log-linear decrease in rating with `eval_randomize `.
    Furthermore, this descrese itself seems to scale with roughly n^(1/4), where n is the match length. So, in our case
    this is not the n^(1/2) that the FIBS rating system employs. (We do not simply have n games to win, but doubling
    strategies play an important role, too.)
    A fit to empirical data yields the rating estimate (2060+-15) - (136+-3) * n^(0.23+-0.01) * log2(eval_randomize),
    as long as eval_randomize >= 2 and the estiamte is >~ 750.
    The above table also implies that the (default) RandomPlayer is about 1000 rating points weaker than the (default)
    SimplePlayer for a single points match (and more for longer games).

    Args:
        doubling_th (float):        Player will double the stake, if they judge the winning probability to be higher
                                    than this number. Conversely, accept a doubling if the winnings probability is
                                    judged to be 1 - <doubling_th>.
        eval_randomize (float):     Make the player play more random moves.
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
            blot_penalty: float = 0.1,
            bear_off_bonus: float = 1.0,
    ):
        super().__init__()
        self.doubling_th = doubling_th
        self.eval_randomize = eval_randomize
        self.win_prob_randomize = win_prob_randomize
        self.blot_penalty = blot_penalty
        self.bear_off_bonus = bear_off_bonus

    def est_win_prob(self, board: Board, viewpoint: Optional[Color] = None) -> float:
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

        if self.eval_randomize:
            win_prob += np.random.normal(scale=self.win_prob_randomize)

        return win_prob

    def eval_board(self, board: Board, viewpoint: Optional[Color] = None, verbose: bool = False) -> float:
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
        if verbose:
            print(f"pip count value: {val} -> {val_tot}")

        # helper variables
        blots_mask = (board.points == viewpoint)
        blots_at = np.where(blots_mask)[0]
        pips_add_if_hit = (25 - blots_at) if viewpoint is Color.WHITE else blots_at
        opponent = viewpoint.other()

        # hit prob. * pips -> avoid own blots
        val = 0
        for p, pips_add in zip(blots_at, pips_add_if_hit):
            # TODO: restrict to legal only / reduce impact of those, that cannot be hit because opponent must clear bar
            val += board.hit_prob(p, opponent) * pips_add
        val_tot -= val
        if verbose:
            print("blots:", blots_mask)
            print("points:", board.points)
            print(f"blot hit loss exp.: {val} -> {val_tot}")

        # penalise blots
        val = self.blot_penalty * blots_mask.sum()
        val_tot -= val
        if verbose:
            print(f"blot ({blots_mask.sum()}) penality: {val} -> {val_tot}")

        # encourage bearing off
        val = self.bear_off_bonus * (15 - board.checkers_count(viewpoint))
        val_tot += val
        if verbose:
            print(f"bear off bonus: {val} -> {val_tot}")

        if self.eval_randomize:
            val_tot += np.random.normal(scale=self.eval_randomize)

        return val_tot

    def eval_action(self, board: Board, action: Action, viewpoint: Optional[Color] = None,
                    verbose: bool = False) -> float:
        # viewpoint of current player, not the one after doing the action!
        if viewpoint is None:
            viewpoint = board.turn
        if viewpoint == Color.NONE:
            raise ValueError(f"viewpoint has to be either Color.BLACK or Color.WHITE, got {viewpoint}")

        do_action(board, action)
        val = self.eval_board(board, viewpoint, verbose=verbose)
        undo_action(board, action)
        return val

    def _choose_action(self, board: Board, dice: NDArray[np.int_]) -> Action:
        actions = build_legal_actions(board, dice)
        act_eval = np.fromiter((self.eval_action(board, action) for action in actions), float)
        best_idx = np.where(act_eval == np.max(act_eval))[0]
        action = actions[np.random.choice(best_idx)]
        return action

    def _will_double(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        # TODO: use points and match_ends_at
        return self.est_win_prob(board) > self.doubling_th

    def _will_take_doubling(self, board: Board, points: NDArray[np.int_], match_ends_at: int) -> bool:
        # TODO: use points and match_ends_at
        th = 1.0 - self.doubling_th
        return self.est_win_prob(board) > th
