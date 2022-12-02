from typing import Iterable, Any
import random

from .defs import Color, GameResult
from .move import Move
from .board import Board
from .legal_moves import build_legal_move, build_legal_moves, IllegalMoveError


class GameState:

    def __init__(
            self,
            board: Board | None = None,
            turn: Color = Color.NONE,
            stake: int = 1,
            doubling_turn: Color = Color.NONE,
            dice: Iterable[int] | None = None,
            dice_used: Iterable[bool] | None = None,
            copy: bool = True,
    ):
        if board is None:
            board = Board()
        self.board = board.copy() if copy else board
        self.turn = turn
        self.stake = stake
        self.doubling_turn = doubling_turn
        self.dice: list[int] = [] if dice is None else list(dice)
        self.dice_used: list[bool] = [True] * len(self.dice) if dice_used is None else list(dice_used)
        if len(self.dice) != len(self.dice_used):
            raise ValueError("lengths of dice and their used state do not match")

    def __hash__(self) -> int:
        # the int cast makes PyCharm happy...
        return hash(self.board) ^ hash(
            (int(self.turn), self.stake, int(self.doubling_turn)) + tuple(self.dice) + tuple(self.dice_used)
        )

    def __getattr__(self, item: str) -> Any:
        return getattr(self.board, item)

    def __dir__(self) -> Iterable[str]:
        return set(super().__dir__()) | set(dir(self.board))

    # def __repr__(self) -> str:
    #     TODO
    #     return NotImplemented

    # def __str__(self) -> str:
    #     return NotImplemented

    def _repr_svg_(self) -> str:
        from ..display import svg_gamestate
        return svg_gamestate(self).tostring()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, GameState) and (
                self.board == other.board
                and self.turn == other.turn
                and self.stake == other.stake
                and self.doubling_turn == other.doubling_turn
                and len(self.dice) == len(other.dice) and all(sd == od for sd, od in zip(self.dice, other.dice))
                and len(self.dice_used) == len(other.dice_used)
                and all(sdu == odu for sdu, odu in zip(self.dice_used, other.dice_used))
        )

    def __copy__(self) -> 'GameState':
        return GameState(self.board, self.turn, self.stake, self.doubling_turn, self.dice, self.dice_used, copy=True)

    def copy(self) -> 'GameState':
        return self.__copy__()

    def flip(self):
        self.board.flip()
        self.turn = self.turn.other()
        self.doubling_turn = self.doubling_turn.other()

    def flipped(self) -> 'GameState':
        copy = self.__copy__()
        copy.flip()
        return copy

    def result(self) -> GameResult:
        winner = self.board.winner()
        wintype = self.board.win_type(looser=winner.other())  # returns WinType.NORMAL, if no winner yet
        return GameResult(winner, self.stake, wintype)

    def can_couble(self, color: Color = Color.NONE) -> bool:
        if color is Color.NONE:
            color = self.turn
        return self.doubling_turn == Color.NONE or self.doubling_turn == color

    def roll_dice(self):
        if self.turn == Color.NONE:
            dice = [1, 1]
            while dice[0] == dice[1]:
                dice = [random.randint(1, 6) for _ in range(2)]
            self.turn = Color.BLACK if dice[0] > dice[1] else Color.WHITE
        else:
            dice = [random.randint(1, 6) for _ in range(2)]

        if dice[0] == dice[1]:
            dice = [dice[0]] * 4
        self.dice = dice
        self.dice_used = [False] * len(dice)

    def build_legal_moves(self) -> list[Move]:
        # build the set to avoid redundancy in move generation
        pips = set(p for p, used in zip(self.dice, self.dice_used) if not used)
        return [m for p in pips for m in build_legal_moves(self.board, p, self.turn)]

    def dice_for_move(self, move: Move) -> int | None:
        for k, pips in enumerate(self.dice):
            if self.dice_used[k]:
                continue

            try:
                m = build_legal_move(self.board, move.src, pips, self.turn)
                if move.pips() <= pips and move == m:
                    return k
            except IllegalMoveError:
                continue

        return None

    def do_move(self, move: Move, k: int | None = None) -> int:
        if k is None:
            k = self.dice_for_move(move)
            if k is None:
                unused_dice = [d for d, u in zip(self.dice, self.dice_used) if not u]
                raise IllegalMoveError(f"{move} is not a legal move, given the (unused) dice {unused_dice}")

        self.dice_used[k] = True
        self.board.do_move(move)
        return k

    def undo_move(self, move: Move, k: int, checked: bool = True):
        if checked:
            assert self.dice_used[k], f"trying to undo a move with unsued die #{k}"
        self.dice_used[k] = False
        self.board.undo_move(move)
        if checked:
            if move != build_legal_move(self.board, move.src, self.dice[k], self.turn):
                raise ValueError(f"{move} does not match die #{k}")

    def finish_turn(self, checked: bool = True):
        if checked:
            assert len(self.build_legal_moves()) == 0, "cannot finish turn, if there are legal moves left"
        self.dice = []
        self.dice_used = []
        self.turn = self.turn.other()
