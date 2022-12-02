import pytest
import numpy as np

from backgammon.core.defs import Color, WinType
from backgammon.core.board import Board
from backgammon.display import board_ascii_art

from .defs import (
    rand_board,
    BOARDS, BOARD_PIP_CNSTS, BOARD_CHECKER_CNT,
    BOARD_REPRS, BOARD_ASCIIS,
    BOARD_GAME_OVER, BOARD_WINNERS, BOARD_WINTYPES,
    BOARD_BEARING_OFF,
)


def test_checkers_init():
    Board()
    with pytest.raises(ValueError):
        Board(np.zeros((2, 5), dtype=int))


@pytest.mark.parametrize('board, expected, idx', zip(BOARDS, BOARD_REPRS, range(100)))
def test_checkers_repr(board: Board, expected: str, idx: int):
    assert repr(board) == expected, f"@ index = {idx}"


@pytest.mark.parametrize('board, expected, idx', zip(BOARDS, BOARD_ASCIIS, range(100)))
def test_checkers_ascii_str(board: Board, expected: str, idx: int):
    assert board_ascii_art(board, info=True, swap_ints=False) == expected, f"@ index = {idx}"
    assert board_ascii_art(board, info=True, swap_ints=False) == str(board), f"@ index = {idx}"


def test_mocked_checkers_svg(mocker):
    # this test will run the creation of the SVG instance, but ignores the actual content
    mocker.patch('svgwrite.Drawing.tostring', return_value='<svg>')
    assert Board()._repr_svg_() == '<svg>'


@pytest.mark.parametrize('board, cnt, idx', zip(BOARDS, BOARD_PIP_CNSTS, range(100)))
def test_pip_cnts(board: Board, cnt: tuple[int, int], idx: int):
    assert all(a == b for a, b in zip(board.pip_count(), cnt))
    assert board.pip_count(Color.BLACK) == cnt[0]
    assert board.pip_count(Color.WHITE) == cnt[1]


@pytest.mark.parametrize('board, cnt, idx', zip(BOARDS, BOARD_CHECKER_CNT, range(100)))
def test_checker_cnts(board: Board, cnt: tuple[int, int], idx: int):
    assert all(a == b for a, b in zip(board.checkers_count(), cnt))
    assert board.checkers_count(Color.BLACK) == cnt[0]
    assert board.checkers_count(Color.WHITE) == cnt[1]


def test_color_at():
    board = BOARDS[0]
    for point, color in [(1, Color.BLACK), (2, Color.NONE), (6, Color.WHITE), (8, Color.WHITE), (14, Color.NONE),
                         (17, Color.BLACK), (18, Color.NONE), (19, Color.BLACK)]:
        assert board.color_at(point) == color

    board = BOARDS[1]
    for point, color in [(1, Color.NONE), (2, Color.WHITE), (3, Color.BLACK), (19, Color.WHITE), (11, Color.NONE)]:
        assert board.color_at(point) == color


def test_checkers_hash():
    n_rand = 5
    hashes = set()
    for board in BOARDS + [rand_board() for _ in range(n_rand)]:
        h = hash(board)
        assert isinstance(h, int)
        hashes.add(h)
    assert len(hashes) > 0.8 * (len(BOARDS) + n_rand), "too many hash collisions"


@pytest.mark.parametrize('board', BOARDS)
def test_checkers_copy(board: Board):
    copy = board.copy()
    assert copy is not board
    assert copy.points is not board.points
    assert copy == board
    copy.points -= 1
    assert np.all(copy.points != board.points)
    assert copy != board


@pytest.mark.parametrize('board', BOARDS[1:])
def test_checkers_flipping(board: Board):
    flipped = board.copy()
    flipped.flip()
    assert flipped.checkers_count(Color.BLACK) == board.checkers_count(Color.WHITE)
    assert flipped.checkers_count(Color.WHITE) == board.checkers_count(Color.BLACK)
    assert flipped.pip_count(Color.BLACK) == board.pip_count(Color.WHITE)
    assert flipped.pip_count(Color.WHITE) == board.pip_count(Color.BLACK)
    assert flipped.winner() == board.winner().other()

    assert flipped.flipped() == board
    flipped.flip()
    assert flipped == board


@pytest.mark.parametrize('board, expect', zip(BOARDS, BOARD_GAME_OVER))
def test_game_over(board: Board, expect: bool):
    assert board.game_over() == expect


@pytest.mark.parametrize('board, exp_win, exp_wt', zip(BOARDS, BOARD_WINNERS, BOARD_WINTYPES))
def test_winners(board: Board, exp_win: Color, exp_wt: tuple[WinType, WinType, WinType]):
    assert board.winner() == exp_win

    wintypes = [board.win_type(looser=c) for c in Color]
    assert all(wt == e for wt, e in zip(wintypes, exp_wt))


@pytest.mark.parametrize('board, pnt, c, expect', [
    (BOARDS[0], 9, Color.WHITE, True),
    (BOARDS[0], 6, Color.BLACK, True),
    (BOARDS[0], 11, Color.NONE, False),
    (BOARDS[1], 25, Color.WHITE, False),
    (BOARDS[1], 20, Color.WHITE, True),
    (BOARDS[2], 25, Color.WHITE, False),
    (BOARDS[2], 20, Color.WHITE, True),
    (BOARDS[3], 21, Color.BLACK, True),
    (BOARDS[3], 21, Color.WHITE, False),
    (BOARDS[4], 11, Color.WHITE, False),
    (BOARDS[5], 21, Color.BLACK, True),
    (BOARDS[5], 1, Color.BLACK, False),
    (BOARDS[6], 9, Color.BLACK, False),
])
def test_checkers_before(board: Board, pnt: int, c: Color, expect: bool):
    assert board.checkers_before(pnt, c) == expect


@pytest.mark.parametrize('board, expects', zip(BOARDS, BOARD_BEARING_OFF))
def test_bearing_off_color(board: Board, expects: tuple[bool, bool]):
    for color, expect in zip([Color.BLACK, Color.WHITE], expects):
        assert board.bearing_off_allowed(color) == expect
    with pytest.raises(ValueError):
        board.bearing_off_allowed(Color.NONE)
