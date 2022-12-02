from typing import Iterable, Any
import random

from ..core import Color, Move, Board, IllegalMoveError
from .move_legal import build_legal_moves, build_legal_move


class GameState:

    def __init__(
            self,
            board: Board | None = None,
            dice: Iterable[int] | None = None,
            dice_unused: Iterable[bool] | None = None,
    ):
        self.board = Board() if board is None else board.copy()
        self.dice: list[int] = [] if dice is None else list(dice)
        self.dice_unused: list[bool] = [True] * len(self.dice) if dice_unused is None else list(dice_unused)
        if len(self.dice) != len(self.dice_unused):
            raise ValueError("lengths of dice and their used state do not match")

    def __hash__(self) -> int:
        return hash(self.board) ^ hash(tuple(self.dice) + tuple(self.dice_unused))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, GameState) and (
                self.board == other.board
                and len(self.dice) == len(other.dice) and all(sd == od for sd, od in zip(self.dice, other.dice))
                and len(self.dice_unused) == len(other.dice_unused)
                and all(sdu == odu for sdu, odu in zip(self.dice_unused, other.dice_unused))
        )

    def __copy__(self) -> 'GameState':
        return GameState(self.board, self.dice, self.dice_unused)

    def copy(self) -> 'GameState':
        return self.__copy__()

    def _repr_svg_(self) -> str:
        from ..display import svg_gamestate
        return svg_gamestate(self).tostring()

    def roll_dice(self):
        if self.board.turn == Color.NONE:
            dice = [1, 1]
            while dice[0] == dice[1]:
                dice = [random.randint(1, 6) for _ in range(2)]
            self.board.turn = Color.BLACK if dice[0] > dice[1] else Color.WHITE
        else:
            dice = [random.randint(1, 6) for _ in range(2)]

        if dice[0] == dice[1]:
            dice = [dice[0]] * 4
        self.dice = dice
        self.dice_unused = [True] * len(dice)

    def build_legal_moves(self) -> list[Move]:
        # build the set to avoid redundancy in move generation
        pips = set(p for p, unused in zip(self.dice, self.dice_unused) if unused)
        return [m for p in pips for m in build_legal_moves(self.board, p)]

    def do_move(self, move: Move) -> int:
        # TODO: rethink, if this checking of a move is appropriate
        i: int | None = None
        for k, pips in enumerate(self.dice):
            if not self.dice_unused[k]:
                continue

            try:
                m = build_legal_move(self.board, move.src, pips)
            except IllegalMoveError:
                continue

            if move.pips() <= pips and move == m:
                self.dice_unused[k] = False
                i = k
                break
        assert i is not None, f"Move {move} not within the legal moves"

        self.board.do_move(move)
        return i

    def undo_move(self, move: Move, i: int):
        assert not self.dice_unused[i]
        self.dice_unused[i] = True
        self.board.undo_move(move)

    def finish_turn(self):
        self.dice = []
        self.dice_unused = []
        self.board.switch_turn()
