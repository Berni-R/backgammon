from typing import Any, Sequence, Optional, Iterator, Union
import numpy as np
from numpy.typing import ArrayLike, NDArray

from ..core import Color, IllegalMoveError
from .move import Move
from ..board import Board
from .move_legal import assert_legal_move, build_legal_move


class Action:

    def __init__(self, moves: Sequence[Move] = (), doubles: int = 0, takes: Optional[bool] = None):
        self.moves = [] if doubles else [m for m in moves]
        self.doubles = doubles
        self.takes = takes

    def __copy__(self) -> 'Action':
        return Action(
            [move for move in self.moves],
            self.doubles,
            self.takes,
        )

    def copy(self) -> 'Action':
        return self.__copy__()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Action) and (
            # set(self.moves) == set(other.moves)
            len(self.moves) == len(other.moves)
            and all(a == b for a, b in zip(self.moves, other.moves))
            and self.doubles == other.doubles
            and self.takes == other.takes
        )

    def __hash__(self) -> int:
        return hash(tuple(self.moves) + (self.doubles, self.takes))

    @property
    def is_dropping(self) -> bool:
        return self.takes is not None and not self.takes

    @property
    def dances(self) -> bool:
        return len(self.moves) == 0 and (not self.doubles)

    def __repr__(self) -> str:
        r = f"Action({self.moves}"
        if self.doubles:
            r += f", doubles={self.doubles}"
        if self.takes is not None:
            r += f", takes={self.takes}"
        return r + ")"

    def to_str(self, bar_off: bool = True, regular: bool = True) -> str:
        if self.takes is not None:
            return 'Takes' if self.takes else 'Drops'
        if self.doubles:
            return f'Doubles => {self.doubles}'
        if len(self.moves) == 0:
            return 'Dances'
        return ' '.join(move.to_str(bar_off, regular) for move in self.moves)

    def __str__(self) -> str:
        return self.to_str()

    def __iter__(self) -> Iterator[Move]:
        return iter(self.moves)

    def __getitem__(self, item: int | slice) -> Union[Move, 'Action']:
        if isinstance(item, int):
            return self.moves[item]
        elif isinstance(item, slice):
            return Action(self.moves[item], self.doubles, self.takes)
        else:
            raise TypeError(f"cannot subscript Action with type {type(item)}")

    def __add__(self, other: 'Action') -> 'Action':
        if self.doubles != 0 or other.doubles:
            raise ValueError("cannot add to doubling actions")
        return Action(self.moves + other.moves)

    def __radd__(self, moves: list[Move]) -> 'Action':
        if self.doubles != 0:
            raise ValueError("cannot (right) add to doubling action")
        return Action(moves + self.moves)


def assert_legal_action(action: Action, board: Board, pseudolegal: bool = False):
    if action.doubles:
        if not pseudolegal:
            if board.doubling_turn is not Color.NONE:
                if action.takes is None:
                    if board.turn != board.doubling_turn:
                        raise IllegalMoveError(f"it is not {board.turn}'s turn to double")
            if action.doubles != 2 * board.stake:
                raise IllegalMoveError(f"'doubling' the stake from {board.stake} to {action.doubles} is illegal")
    else:
        test_board = board.copy()
        for move in action:
            assert_legal_move(move, test_board, pseudolegal=pseudolegal)
            test_board.do_move(move)


def is_legal_action(action: Action, board: Board, pseudolegal: bool = False) -> bool:
    try:
        assert_legal_action(action, board, pseudolegal=pseudolegal)
    except IllegalMoveError:
        return False
    return True


def do_action(board: Board, action: Action):
    if action.doubles:
        if action.takes:
            board.stake *= 2
            board.doubling_turn = board.turn
    else:
        for move in action:
            board.do_move(move)
    board.switch_turn()


def undo_action(board: Board, action: Action):
    board.switch_turn()
    if action.doubles:
        if action.takes:
            board.stake //= 2
            board.doubling_turn = Color.NONE if board.stake == 1 else board.turn.other()
    else:
        for move in action.moves[::-1]:
            board.undo_move(move)


def _legal_actions(board: Board, dice: Sequence, src_lim: Optional[int] = None) -> list[Action]:
    """Does not include a potential doubling."""
    sources: NDArray | list = np.where(np.sign(board.points) == np.array(board.turn))[0]

    # avoid equivalent multiplications
    if board.turn is Color.WHITE:
        src_lim = src_lim or 25
        sources = [src for src in sources if src <= src_lim]
    if board.turn is Color.BLACK:
        src_lim = src_lim or 0
        sources = [src for src in sources if src >= src_lim]

    actions = []
    for src in sources:
        # try building a legal move with given source and die
        try:
            move = build_legal_move(board, src, dice[0])
        except IllegalMoveError:
            continue

        # if there are more dice, continue building the action
        if len(dice) > 1:
            board.do_move(move)
            act = _legal_actions(board, dice[1:], src_lim=src)
            board.undo_move(move)
            actions += [[move] + a for a in act]
        else:
            # otherwise we are done here
            actions += [Action([move])]

    return actions


def _unique_actions(board: Board, actions: list[Action]) -> list[Action]:
    final_boards: set[int] = set()

    u_actions = []
    for action in actions:
        do_action(board, action)
        if hash(board) not in final_boards:
            final_boards.add(hash(board))
            u_actions.append(action)
        undo_action(board, action)

    return u_actions


def build_legal_actions(board: Board, dice: ArrayLike) -> list[Action]:
    """Does not include a potential doubling."""
    # TODO: update algo, since not efficient for double rolls, because of the many equivalent permutations
    dice = np.array(dice, dtype=int)
    assert dice.shape == (2,)

    if board.turn is Color.NONE:
        raise ValueError("It's no ones turn, cannot build legal actions.")

    if dice[0] == dice[1]:
        # double roll
        for n in [4, 3, 2, 1]:
            actions = _legal_actions(board, [dice[0]] * n)
            if len(actions):
                break
    else:
        # rolled two different numbers
        actions = _legal_actions(board, list(dice)) + _legal_actions(board, list(dice[::-1]))
        if len(actions) == 0:
            actions = _legal_actions(board, [dice[0]]) + _legal_actions(board, [dice[1]])

    if len(actions) == 0:
        actions = [Action()]
    else:
        actions = _unique_actions(board, actions)

    return actions
