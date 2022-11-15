from typing import Sequence, Optional
import numpy as np
from numpy.typing import ArrayLike, NDArray

from ..core import Color, IllegalMoveError
from ..board import Board
from .move_legal import assert_legal_move, build_legal_move
from .action import Action


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
