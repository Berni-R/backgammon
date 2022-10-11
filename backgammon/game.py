from typing import Optional
from numpy.typing import NDArray, ArrayLike
from copy import deepcopy
import numpy as np

from .core import Color, GameResult
from .board import Board
from .players import Player
from .legal_actions import Action, do_action, is_legal_action


def roll_dice() -> NDArray[np.int_]:
    return np.random.randint(1, 7, size=(2,))


class History(list[tuple[NDArray[np.int_], Action]]):

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
    # TODO: implement automatic doubling, beavers, Jacoby Rule
    # TODO: might want to let player check, previous move was legal or accept otherwise

    def __init__(self, black: Player, white: Player, start_board: Optional[Board] = None):
        self.black = black
        self.white = white
        self.board = Board() if start_board is None else start_board.copy()
        self._history: History = History()
        self._first_move_color = Color.NONE

    def __len__(self) -> int:
        return len(self._history)

    def color_began(self) -> Color:
        return self._first_move_color

    def resigned(self) -> bool:
        if len(self._history) == 0:
            return False
        _, action = self._history[-1]
        return action.is_dropping

    def game_over(self) -> bool:
        return self.resigned() or self.board.game_over()

    def winner(self) -> Color:
        if self.resigned():
            return self.board.turn
        return self.board.winner()

    def get_result(self) -> GameResult:
        if self.resigned():
            winner = self.board.turn
            return GameResult(
                winner=winner,
                doubling_cube=self.board.stake,
                # gammon=self.board.is_gammon(winner.other()),
                # backgammon=self.board.is_backgammon(winner.other()),
            )
        else:
            return self.board.result()

    def get_history(self) -> History:
        return deepcopy(self._history)

    def roll_dice(self) -> NDArray[np.int_]:
        if self.board.turn is Color.NONE:
            dice = np.ones(2, dtype=int)
            while dice[0] == dice[1]:
                dice = roll_dice()
            self.board.turn = Color.BLACK if dice[0] > dice[1] else Color.WHITE
            self._first_move_color = self.board.turn
            return dice
        else:
            return roll_dice()

    @property
    def turn(self) -> Color:
        return self.board.turn

    def next_has_to_respond_to_doubling(self) -> bool:
        if len(self._history) == 0:
            return False
        _, action = self._history[-1]
        return action.doubles > 0 and action.takes is None

    def do_turn(self, points: ArrayLike = (0, 0), match_ends_at: int = 1) -> tuple[NDArray[np.int_], Action]:
        # need to first roll dice, because first roll needed to determine player to begin
        dice = self.roll_dice()
        player = self.white if self.board.turn == Color.WHITE else self.black
        if self.next_has_to_respond_to_doubling():
            action = player.respond_to_doubling(self.board)
        else:
            action = player.play(self.board, dice, points, match_ends_at)
        is_legal_action(action, self.board, raise_except=True)
        do_action(self.board, action)
        self._history.append((dice.copy(), action.copy()))
        return dice, action
