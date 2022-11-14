from typing import Optional, Iterable, Callable, Any
import numpy as np
from numpy.typing import NDArray
from tqdm.auto import tqdm  # type: ignore

from .core import Color
from .board import Board
from .moves.legal_actions import Action
from .game import Game
from .players import Player

MoveHook = Callable[[Game, Action], bool]
GameHook = Callable[[Game], bool]


class Match:

    def __init__(
            self,
            black: Player,
            white: Player,
            n_points: int = 1,
            start_board: Optional[Board] = None,
    ):
        self.black = black
        self.white = white
        self.n_points = n_points
        self.start_board = start_board

        self.points = np.array([0, 0])
        self.games: list[Game] = []

        self._current_game: Optional[Game] = None  # useful for debugging

    def play_single_game(self, after_move: Iterable['MoveHook'] = ()) -> Game:
        game = Game(black=self.black, white=self.white, start_board=self.start_board)
        self._current_game = game
        while not game.game_over():
            dice, action = game.do_turn(self.points, self.n_points)
            if any([hook(game, action) for hook in after_move]):
                break

        self.games.append(game)
        res = game.get_result()
        stake = 0 if res.winner is Color.NONE else res.stake
        self.points[(res.winner + 1) // 2] += stake

        self._current_game = None

        return game

    def play(
            self,
            after_move: Iterable['MoveHook'] = (),
            after_game: Iterable['GameHook'] = (),
            tqdm_disable: bool = False,
            tqdm_args: Optional[dict[str, Any]] = None,
    ):
        args = dict(unit='points', smoothing=0.05, disable=tqdm_disable)
        if tqdm_args is not None:
            args.update(tqdm_args)

        with tqdm(total=self.n_points, **args) as pbar:
            while pbar.n < pbar.total:
                game = self.play_single_game(after_move)

                pbar.n = np.max(self.points)
                pbar.set_postfix({
                    'BLACK': self.points[0],
                    'WHITE': self.points[1],
                    '#games': len(self.games),
                }, refresh=True)

                if any([hook(game) for hook in after_game]):
                    break

    def get_num_wins(self) -> NDArray[np.int_]:
        winners = [[game.winner() == Color.BLACK, game.winner() == Color.WHITE] for game in self.games]
        return np.sum(winners, axis=0)

    def get_winner(self) -> Color:
        if self.points[0] == self.points[1]:
            raise RuntimeError("Both players have the same number of points!")
        return Color(2 * int(np.argmax(self.points)) - 1)

    def print_stats(self):
        wins = self.get_num_wins()
        n_games = len(self.games)

        print("BLACK:", str(self.black))
        print("WHITE:", str(self.white))
        print()
        print(f"stats of {n_games:,d} games (until >={self.n_points}):")
        print()
        print("         | BLACK | WHITE | WHITE AVG. ")
        print("---------|-------|-------|------------")
        print(f"points   | {self.points[0]:5d} | {self.points[1]:5d} | {self.points[1] / n_games:10.2f} ")
        print(f"wins     | {wins[0]:5d} | {wins[1]:5d} | {wins[1] / n_games:10.1%} ")
        stakes = np.array([game.get_result().stake for game in self.games])
        winners = np.array([game.winner() for game in self.games])
        print("---------|-------|-------|------------")
        print("         | BLACK | WHITE | WHITE AVG. ")
        print("---------|-------|-------|------------")
        for stake in np.unique(stakes):
            w = np.array([[winner == Color.BLACK, winner == Color.WHITE]
                          for winner in winners[stakes == stake]]).sum(axis=0)
            print(f"   {stake:5d} | {w[0]:5d} | {w[1]:5d} | {w[1] / w.sum():10.1%} ")
