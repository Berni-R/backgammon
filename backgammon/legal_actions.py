from typing import List, Set, Tuple, Any, Union, Sequence, Optional, Iterator
from copy import copy
import numpy as np
from numpy.typing import ArrayLike

from .core import Color, IllegalMoveError, ImpossibleMoveError
from .move import Move
from .board import Board

__all__ = [
    'Action',
    'build_legal_move', 'build_legal_moves',
    'is_legal_move', 'is_legal_action',
    'do_action', 'undo_action',
    'build_legal_actions',
]


class Action:

    def __init__(self, moves: Sequence[Move] = (), doubles: int = 0, takes: Optional[bool] = None):
        self.moves = [] if doubles else moves
        self.doubles = doubles
        self.takes = takes

    def __copy__(self) -> 'Action':
        return Action(
            [copy(move) for move in self.moves],
            self.doubles,
            self.takes,
        )

    def copy(self) -> 'Action':
        return self.__copy__()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Action) and (
            len(self.moves) == len(other.moves)
            and all(m1 == m2 for m1, m2 in zip(self.moves, other.moves))
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
        r = f"Action({list(self.moves)}"
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

    def __getitem__(self, item: Union[int, slice]) -> Union[Move, 'Action']:
        if isinstance(item, int):
            return self.moves[item]
        elif isinstance(item, slice):
            return Action(self.moves[item], self.doubles, self.takes)
        else:
            raise TypeError(f"cannot subscript Action with type {type(item)}")

    def __radd__(self, move: Move) -> 'Action':
        if self.doubles != 0:
            raise ValueError("cannot (right) add move to doubling action")
        return Action([move] + list(self.moves))


def build_legal_move(board: Board, src: int, pips: int) -> Move:
    color = board.color_at(src)
    if color == Color.NONE:
        raise ImpossibleMoveError(f"no checkers to move from index {src}")

    if board.turn != Color.NONE and color != board.turn:
        raise IllegalMoveError(f"checker's color {color} on {src} does not match board turn {board.turn}")

    if ((color == Color.WHITE and board[25] > 0 and src != 25)
            or (color == Color.BLACK and board[0] < 0 and src != 0)):
        raise IllegalMoveError(f"checkers on bar need to be moved first for {color}")

    # naive move
    dst = src - color * pips
    hit = False

    if dst <= 0 or 25 <= dst:
        # bearing off - if it is allowed
        if not board.bearing_off_allowed(color):
            raise IllegalMoveError(f"bearing off when not all checkers on home board is not allowed (turn: {color})")
        if dst not in (0, 25):
            if board.checkers_before(src, color):
                raise IllegalMoveError(f"need (still) to bear off exactly from {src}")
            dst = max(0, min(dst, 25))
    else:
        # move on regular point - check if not blocked / hit
        n_dst = board[dst]
        if -n_dst * color > 1:
            raise IllegalMoveError(f"destination point {dst} is blocked by other color")
        elif n_dst == -color:
            hit = True

    return Move(src, dst, hit)


def build_legal_moves(board: Board, pips: int) -> List[Move]:
    if not 1 <= pips <= 6:
        raise ValueError(f"pips / dice number must be 1, 2, 3, 4, 5, or 6; got {pips}")

    moves = []
    for start in range(26):
        try:
            m = build_legal_move(board, start, pips)
            moves.append(m)
        except IllegalMoveError:
            pass

    return moves


def is_legal_move(move: Move, board: Board, ret_reason: bool = False) -> Union[bool, Tuple[bool, str]]:
    try:
        build_legal_move(board, move.src, move.pips)
    except IllegalMoveError as e:
        return (False, str(e)) if ret_reason else False
    return (True, "legal") if ret_reason else True


def is_legal_action(action: Action, board: Board,
                    ret_reason: bool = False, raise_except: bool = False) -> Union[bool, Tuple[bool, str]]:
    if action.doubles:
        if board.doubling_turn is not Color.NONE:
            if action.takes is None:
                if board.turn != board.doubling_turn:
                    msg = f"it is not {board.turn}'s turn to double"
                    if raise_except:
                        raise IllegalMoveError(msg)
                    return (False, msg) if ret_reason else False
        if action.doubles != 2 * board.stake:
            msg = f"'doubling' the stake from {board.stake} to {action.doubles} is illegal"
            if raise_except:
                raise IllegalMoveError(msg)
            return (False, msg) if ret_reason else False
    else:
        test_board = board.copy()
        for move in action:
            try:
                build_legal_move(test_board, move.src, move.pips)
            except IllegalMoveError as e:
                if raise_except:
                    raise e
                return (False, str(e)) if ret_reason else False
            test_board.do_move(move)
    return (True, "legal") if ret_reason else True


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


def _legal_actions(board: Board, dice: ArrayLike) -> List[Action]:
    """Does not include a potential doubling."""
    dice = np.array(dice, dtype=int)
    assert dice.ndim == 1

    if board.turn is Color.NONE:
        raise ValueError("Cannot generate actions, if it's no-one's turn")

    if len(dice) == 0:
        return [Action()]

    actions = []
    for move in build_legal_moves(board, dice[0]):
        board.do_move(move)
        act = _legal_actions(board, dice[1:])
        board.undo_move(move)
        actions += [move + a for a in act]
    if len(actions) == 0:
        actions = [Action()]

    return actions


def _unique_actions(board: Board, actions: List[Action]) -> List[Action]:
    final_boards: Set[int] = set()

    u_actions = []
    for action in actions:
        do_action(board, action)
        if hash(board) not in final_boards:
            final_boards.add(hash(board))
            u_actions.append(action)
        undo_action(board, action)

    return u_actions


def build_legal_actions(board: Board, dice: ArrayLike) -> List[Action]:
    """Does not include a potential doubling."""
    # TODO: update algo, since not efficient for double rolls, because of the many equivalent permutations
    dice = np.array(dice, dtype=int)
    assert dice.shape == (2,)

    if dice[0] == dice[1]:
        actions = _legal_actions(board, [dice[0]] * 4)
    else:
        actions = _legal_actions(board, dice) + _legal_actions(board, dice[::-1])

    return _unique_actions(board, actions)
