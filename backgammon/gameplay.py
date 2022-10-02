from typing import Optional, List, Tuple
from copy import deepcopy
import numpy as np

from .core import Color, GameResult, IllegalMoveError
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

    @property
    def game_over(self) -> bool:
        return self._board.game_over()

    def get_result(self) -> GameResult:
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

    def do_turn(self):
        dice = self.roll_dice()
        player = self.white if self._board.turn == Color.WHITE else self.black
        action = player.choose_action(self._board, dice)
        is_legal_action(action, self._board, raise_except=True)
        do_action(self._board, action)
        self._history.append((dice, action))
