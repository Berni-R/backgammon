from typing import Iterable
import numpy as np

from backgammon.core import Color, WHITE_BAR, BLACK_BAR, ImpossibleMoveError, IllegalMoveError
from backgammon.core import Move, Board


def assert_legal_move(move: Move, board: Board, turn: Color = Color.NONE):
    """Assert that the given move is legal. (Includes checking the `hit` property.)"""
    if move.src < 0 or 25 < move.src:
        raise ImpossibleMoveError(f"move source {move.src} not on board")
    if move.dst < 0 or 25 < move.dst:
        raise ImpossibleMoveError(f"move destination {move.src} not on board")

    color = board.color_at(move.src)
    if color == Color.NONE:
        raise ImpossibleMoveError(f"no checkers to move from index {move.src}")

    if (move.dst - move.src) * color > 0:
        raise IllegalMoveError(f"move direction ({move.src} -> {move.dst}) in wrong direction for color ({color})")

    if move.bearing_off():
        if not board.bearing_off_allowed(color):
            raise IllegalMoveError(f"bearing off when not all checkers on home board is not allowed (turn: {color})")
        if move.hit is True:
            raise ImpossibleMoveError("`Move.hit` is True for a bearing off move")
    else:
        # move on regular point - check if not blocked / hit
        n_dst = board.points[move.dst]
        if n_dst * color < -1:
            raise IllegalMoveError(f"destination point {move.dst} is blocked by other color")
        elif move.hit != (n_dst == -color):
            negate = 'not ' if move.hit else ''
            raise ImpossibleMoveError(f"`hit` property of move does not match (actually {negate}hitting)")

    if turn != Color.NONE and color != turn:
        raise IllegalMoveError(f"checker's color {color} on {move.src} does not match turn {turn}")

    if ((color == Color.WHITE and board.points[WHITE_BAR] > 0 and move.src != WHITE_BAR)
            or (color == Color.BLACK and board.points[BLACK_BAR] < 0 and move.src != BLACK_BAR)):
        raise IllegalMoveError(f"checkers on bar need to be moved first for {color}")


def is_legal_move(move: Move, board: Board, turn: Color = Color.NONE) -> bool:
    """Check if the given move is legal. (Includes checking the `hit` property.)"""
    try:
        assert_legal_move(move, board, turn)
    except IllegalMoveError:
        return False
    return True


def build_legal_move(board: Board, src: int, pips: int, turn: Color = Color.NONE) -> Move:
    """Build a legal move that starts at `src` using a die with `pips` eyes."""
    color = board.color_at(src)
    if color == Color.NONE:
        raise ImpossibleMoveError(f"no checkers to move from index {src}")
    if turn != Color.NONE and color != turn:
        raise IllegalMoveError(f"checker's color {color} on {src} does not match turn {turn}")

    dst = src - color * pips
    if dst < 0 or 25 < dst:
        if board.checkers_before(src, color):
            raise IllegalMoveError(f"(still) need to bear off exactly from {src}")
        dst = max(0, min(dst, 25))

    hit = (0 < dst < 25) and bool(board.points[dst] == -color.value)
    move = Move(src, dst, hit)

    if move.bearing_off():
        if not board.bearing_off_allowed(color):
            raise IllegalMoveError(f"bearing off when not all checkers on home board is not allowed (turn: {color})")
    else:
        # move on regular point - check if not blocked / hit
        n_dst = board.points[move.dst]
        if n_dst * color.value < -1:
            raise IllegalMoveError(f"destination point {move.dst} is blocked by other color")

    if ((color == Color.WHITE and board.points[WHITE_BAR] > 0 and move.src != WHITE_BAR)
            or (color == Color.BLACK and board.points[BLACK_BAR] < 0 and move.src != BLACK_BAR)):
        raise IllegalMoveError(f"checkers on bar need to be moved first for {color}")

    return move


def build_legal_moves(board: Board, pips: int, color: Color) -> list[Move]:
    """Build all legal game that that use a die with `pips` eyes."""
    if color == Color.NONE:
        sources: Iterable[int] = range(26)
    else:
        if color == Color.WHITE and board.points[WHITE_BAR] > 0:
            sources = [WHITE_BAR]
        elif color == Color.BLACK and board.points[BLACK_BAR] < 0:
            sources = [BLACK_BAR]
        else:
            sources = np.where(np.sign(board.points) == color.value)[0]

    moves = []
    for src in sources:
        try:
            m = build_legal_move(board, src, pips, color)
            moves.append(m)
        except IllegalMoveError:
            pass

    return moves
