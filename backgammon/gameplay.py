from typing import Optional, List, Tuple
from copy import deepcopy
import numpy as np

from .core import Color, GameResult
from .board import Board
from .players import Player
from .legal import Action, do_action, is_legal_action


def roll_dice() -> np.ndarray:
    return np.random.randint(1, 7, size=(2,))


class History(List[Tuple[np.ndarray, Action]]):

    def __repr__(self):
        return f"<History, len={len(self)}>"

    def show(self, **kwargs):
        ply = 0
        for dice, action in self:
            if action.doubles:
                act = f"{str(action):33s}"
            else:
                act = f"{dice[0]}-{dice[1]}: {str(action):28s}"
            if ply % 2 == 0:
                print(f"{ply // 2 + 1:3d}) {act}", end=' ', **kwargs)
            else:
                print(f"{act}", **kwargs)
            ply += 1


class Game:

    def __init__(self, white: Player, black: Player, start_board: Optional[Board] = None):
        self.white = white
        self.black = black
        self._board = Board() if start_board is None else start_board.copy()
        self._history: History = History()

    def __len__(self) -> int:
        return len(self._history)

    def get_board(self) -> Board:
        return self._board.copy()

    def resigned(self) -> bool:
        if len(self._history) == 0:
            return False
        _, action = self._history[-1]
        return action.takes is False

    def game_over(self) -> bool:
        return self.resigned() or self._board.game_over()

    def get_result(self) -> GameResult:
        if self.resigned():
            winner = self._board.turn
            return GameResult(
                winner=winner,
                doubling_cube=self._board.stake,
                # gammon=self._board.is_gammon(winner.other()),
                # backgammon=self._board.is_backgammon(winner.other()),
            )
        else:
            return self._board.result()

    def get_history(self) -> History:
        return deepcopy(self._history)

    def roll_dice(self) -> np.ndarray:
        if self._board.turn is Color.NONE:
            dice = np.ones(2, dtype=int)
            while dice[0] == dice[1]:
                dice = roll_dice()
            self._board.turn = Color.BLACK if dice[0] > dice[1] else Color.WHITE
            return dice
        else:
            return roll_dice()

    @property
    def turn(self) -> Color:
        return self._board.turn

    def next_has_to_respond_to_doubling(self) -> bool:
        if len(self._history) == 0:
            return False
        _, action = self._history[-1]
        return action.doubles > 0 and action.takes is None

    def do_turn(self):
        # need to first roll dice, because first roll needed to determine player to begin
        dice = self.roll_dice()
        player = self.white if self._board.turn == Color.WHITE else self.black
        if self.next_has_to_respond_to_doubling():
            action = player.respond_to_doubling(self._board)
            assert action.takes is not None
        else:
            action = player.choose_action(self._board, dice)
        is_legal_action(action, self._board, raise_except=True)
        do_action(self._board, action)
        self._history.append((dice, action))
