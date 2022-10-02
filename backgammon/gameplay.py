from typing import List, Set
import numpy as np
from numpy.typing import ArrayLike

from .core import Color, IllegalMoveError, ImpossibleMoveError
from .move import Move
from .board import Board


def build_legal_move(board: Board, src: int, pips: int) -> Move:
    color = board.color_at(src)
    if color == Color.NONE:
        raise ImpossibleMoveError(f"no checkers to move from index {src}")

    if board.turn != Color.NONE and color != board.turn:
        raise IllegalMoveError(f"checker's color {color} does not match board turn {board.turn}")

    if ((color == Color.WHITE and board[25] > 0 and src != 25)
            or (color == Color.BLACK and board[0] < 0 and src != 0)):
        raise IllegalMoveError("checkers on bar need to be moved first")

    # naive move
    dst = src - color.value * pips
    hit = False

    if dst <= 0 or 25 <= dst:
        # bearing off - if it is allowed
        if not board.bearing_off_allowed(color):
            raise IllegalMoveError("bearing off when not all checkers on home board not allowed")
        if dst not in (0, 25):
            if board.checkers_before(src, color):
                raise IllegalMoveError(f"need (still) to bear off exactly from {src}")
            dst = max(0, min(dst, 25))
    else:
        # move on regular point - check if not blocked / hit
        n_dst = board[dst]
        if -n_dst * color.value > 1:
            raise IllegalMoveError(f"destination point {dst} is blocked by other color")
        elif n_dst == -color.value:
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


def do_action(board: Board, action: List[Move]):
    for move in action:
        board.do_move(move)
    board.switch_turn()


def undo_action(board: Board, action: List[Move]):
    board.switch_turn()
    for move in action[::-1]:
        board.undo_move(move)


def _legal_actions(board: Board, dice: ArrayLike) -> List[List[Move]]:
    dice = np.array(dice, dtype=int)
    assert dice.ndim == 1

    if board.turn is Color.NONE:
        raise ValueError("Cannot generate actions, if it's no-one's turn")

    if len(dice) == 0:
        return [[]]

    actions = []
    for move in build_legal_moves(board, dice[0]):
        board.do_move(move)
        act = _legal_actions(board, dice[1:])
        board.undo_move(move)
        actions += [[move] + a for a in act]
    if len(actions) == 0:
        actions = [[]]

    return actions


def _unique_actions(board: Board, actions: List[List[Move]]) -> List[List[Move]]:
    final_boards: Set[int] = set()

    u_actions = []
    for action in actions:
        do_action(board, action)
        if hash(board) not in final_boards:
            final_boards.add(hash(board))
            u_actions.append(action)
        undo_action(board, action)

    return u_actions


def legal_actions(board: Board, dice: ArrayLike) -> List[List[Move]]:
    # TODO: update algo, since not efficient for double rolls, because of the many equivalent permutations
    dice = np.array(dice, dtype=int)
    assert dice.shape == (2,)

    if dice[0] == dice[1]:
        actions = _legal_actions(board, [dice[0]] * 4)
    else:
        actions = _legal_actions(board, dice) + _legal_actions(board, dice[::-1])

    return _unique_actions(board, actions)
