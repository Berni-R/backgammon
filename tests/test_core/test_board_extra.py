import pytest

from backgammon.core.defs import Color, WinType
from backgammon.core.board import Board

from .defs import (
    BOARDS, BOARD_BEARING_OFF, BOARD_BEARING_OFF_TURN, BOARD_CAN_COUBLE,
    BOARD_GAME_OVER, BOARD_WINNERS, BOARD_WINTYPES,
)


@pytest.mark.parametrize('board, expect', zip(BOARDS, BOARD_GAME_OVER))
def test_game_over(board: Board, expect: bool):
    assert board.game_over() == expect


@pytest.mark.parametrize('board, exp_win, exp_wt', zip(BOARDS, BOARD_WINNERS, BOARD_WINTYPES))
def test_results(board: Board, exp_win: Color, exp_wt: tuple[WinType, WinType, WinType]):
    assert board.winner() == exp_win

    wintypes = [board.win_type(looser=c) for c in Color]
    assert all(wt == e for wt, e in zip(wintypes, exp_wt))

    res = board.result()
    assert res.winner == exp_win
    assert res.wintype == board.win_type(looser=exp_win.other())
    assert res.doubling_cube == board.stake


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


@pytest.mark.parametrize('board, expect', zip(BOARDS, BOARD_BEARING_OFF_TURN))
def test_bearing_off_turn(board: Board, expect: bool | None):
    if expect is None:
        with pytest.raises(ValueError):
            board.bearing_off_allowed()
    else:
        assert board.bearing_off_allowed() == expect


@pytest.mark.parametrize('board, expect', zip(BOARDS, BOARD_CAN_COUBLE))
def test_can_double(board: Board, expect: bool):
    assert board.can_couble() == expect
