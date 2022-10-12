from .core import Color, ImpossibleMoveError, IllegalMoveError
from .move import Move
from .board import Board


def assert_legal_move(move: Move, board: Board, pseudolegal: bool = False):
    """Assert that the given move is (pseudo-)legal. (Includes checking the `hit` property.)"""
    if move.src < 0 or 25 < move.src:
        raise ImpossibleMoveError(f"move source {move.src} not on board")
    if move.dst < 0 or 25 < move.dst:
        raise ImpossibleMoveError(f"move destination {move.src} not on board")

    color = board.color_at(move.src)
    if color == Color.NONE:
        raise ImpossibleMoveError(f"no checkers to move from index {move.src}")

    if move.dst not in (0, 25):
        # move on regular point - check if not blocked / hit
        n_dst = board.points[move.dst]
        if -n_dst * color > 1:
            raise IllegalMoveError(f"destination point {move.dst} is blocked by other color")
        elif move.hit != (n_dst == -color):
            negate = 'not ' if move.hit else ''
            raise ImpossibleMoveError(f"`hit` property of move does not match (actually {negate}hitting)")
    elif move.hit is True:
        raise ImpossibleMoveError("`Move.hit` is True for a bearing off move")

    if not pseudolegal:
        if not 1 <= move.pips <= 6:
            raise IllegalMoveError(f"would not move 1 - 6 pips, but {move.pips}")

        if board.turn != Color.NONE and color != board.turn:
            raise IllegalMoveError(f"checker's color {color} on {move.src} does not match board turn {board.turn}")

        if ((color == Color.WHITE and board[25] > 0 and move.src != 25)
                or (color == Color.BLACK and board[0] < 0 and move.src != 0)):
            raise IllegalMoveError(f"checkers on bar need to be moved first for {color}")

        if move.dst in (0, 25) and not board.bearing_off_allowed(color):
            raise IllegalMoveError(f"bearing off when not all checkers on home board is not allowed (turn: {color})")


def is_legal_move(move: Move, board: Board, pseudolegal: bool = False) -> bool:
    """Check if the given move is (pseudo-)legal. (Includes checking the `hit` property.)"""
    try:
        assert_legal_move(move, board, pseudolegal=pseudolegal)
    except IllegalMoveError:
        return False
    return True


def build_legal_move(board: Board, src: int, pips: int, pseudolegal: bool = False) -> Move:
    """Build a (pseudo-)legal move that starts at `src` using a die with `pips` eyes."""
    color = board.color_at(src)
    if color == Color.NONE:
        raise ImpossibleMoveError(f"no checkers to move from index {src}")

    dst = src - color * pips
    if dst < 0 or 25 < dst:
        if not pseudolegal and board.checkers_before(src, color):
            raise IllegalMoveError(f"need (still) to bear off exactly from {src}")
        dst = max(0, min(dst, 25))

    hit = (0 < dst < 25) and bool(board.points[dst] == -color)

    move = Move(src, dst, hit)
    assert_legal_move(move, board, pseudolegal=pseudolegal)

    return move


def build_legal_moves(board: Board, pips: int, pseudolegal: bool = False) -> list[Move]:
    """Build all (pseudo-)legal moves that that use a die with `pips` eyes."""
    if not 1 <= pips <= 6:
        raise ValueError(f"pips / dice number must be 1, 2, 3, 4, 5, or 6; got {pips}")

    moves = []
    for src in range(26):
        try:
            m = build_legal_move(board, src, pips, pseudolegal=pseudolegal)
            moves.append(m)
        except IllegalMoveError:
            pass

    return moves
