from typing import Iterable, Callable, Any
import numpy as np
from numpy.typing import NDArray
from tqdm.auto import tqdm  # type: ignore

from ..core import Color, GameState
from .agent import Agent
from .game import Game, Action

MoveHook = Callable[[Game, list[int], Action | None], bool]
GameHook = Callable[[Game], bool]


class Match:

    def __init__(
            self,
            agents: Agent | dict[Color, Agent],
            n_points: int = 1,
            allow_doubling: bool = True,
            start_start: GameState | None = None,
    ):
        if isinstance(agents, Agent):
            agents = {Color.BLACK: agents, Color.WHITE: agents}
        self.agents: dict[Color, Agent] = agents
        self.n_points = n_points
        self.allow_doubling = allow_doubling
        self.start_state = start_start

        self.points = [0, 0]
        self.games: list[Game] = []

        self._current_game: Game | None = None  # useful for debugging

    def play_single_game(self, after_move: Iterable[MoveHook] = ()) -> Game:
        game = Game(state=self.start_state)
        self._current_game = game
        while not game.game_over():
            action = game.step(
                self.agents,
                points=self.points,
                match_ends_at=self.n_points,
                allow_doubling=self.allow_doubling,
            )
            if any([hook(game, game.state.dice, action) for hook in after_move]):
                break

        self.games.append(game)
        res = game.result()
        if res.winner is not Color.NONE:
            self.points[(res.winner + 1) // 2] += res.stake

        self._current_game = None

        return game

    def play(
            self,
            after_move: Iterable[MoveHook] = (),
            after_game: Iterable[GameHook] = (),
            tqdm_disable: bool = False,
            tqdm_args: dict[str, Any] | None = None,
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
        winners = [[game.result().winner == Color.BLACK, game.result().winner == Color.WHITE] for game in self.games]
        return np.sum(winners, axis=0)

    def get_winner(self) -> Color:
        if self.points[0] == self.points[1]:
            raise RuntimeError("Both players have the same number of points!")
        return Color(2 * int(np.argmax(self.points)) - 1)

    def print_stats(self):
        wins = self.get_num_wins()
        n_games = len(self.games)

        print("BLACK:", str(self.agents[Color.BLACK]))
        print("WHITE:", str(self.agents[Color.WHITE]))
        print()
        print(f"stats of {n_games:,d} games (until >={self.n_points}):")
        print()
        print("         | BLACK | WHITE | WHITE AVG. ")
        print("---------|-------|-------|------------")
        print(f"points   | {self.points[0]:5d} | {self.points[1]:5d} | {self.points[1] / n_games:10.2f} ")
        print(f"wins     | {wins[0]:5d} | {wins[1]:5d} | {wins[1] / n_games:10.1%} ")
        stakes = np.array([game.result().stake for game in self.games])
        winners = np.array([game.result().winner for game in self.games])
        print("---------|-------|-------|------------")
        print("         | BLACK | WHITE | WHITE AVG. ")
        print("---------|-------|-------|------------")
        for stake in np.unique(stakes):
            w = np.array([[winner == Color.BLACK, winner == Color.WHITE]
                          for winner in winners[stakes == stake]]).sum(axis=0)
            print(f"   {stake:5d} | {w[0]:5d} | {w[1]:5d} | {w[1] / w.sum():10.1%} ")
