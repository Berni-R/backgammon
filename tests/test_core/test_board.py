import pytest
import random
import numpy as np

from backgammon.core.defs import Color
from backgammon.core.board import Board
from backgammon.display import board_ascii_art

from .defs import (
    rand_board,
    BOARDS, BOARD_PIP_CNSTS, BOARD_CHECKER_CNT,
    BOARD_REPRS, BOARD_ASCIIS,
)


def test_board_init():
    Board()
    with pytest.raises(ValueError):
        Board(np.zeros((2, 5), dtype=int))


@pytest.mark.parametrize('board, expected, idx', zip(BOARDS, BOARD_REPRS, range(100)))
def test_board_repr(board: Board, expected: str, idx: int):
    assert repr(board) == expected, f"@ index = {idx}"


@pytest.mark.parametrize('board, expected, idx', zip(BOARDS, BOARD_ASCIIS, range(100)))
def test_board_ascii_str(board: Board, expected: str, idx: int):
    assert board_ascii_art(board, info=True, swap_ints=False) == expected, f"@ index = {idx}"
    assert board_ascii_art(board, info=True, swap_ints=False) == str(board), f"@ index = {idx}"


def test_mocked_board_svg(mocker):
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


@pytest.mark.parametrize('power', [0, 1, 2, 3, 4])
def test_stake_setting(power: int):
    board = random.choice(BOARDS)

    board.stake = 2 ** power
    assert board.stake == 2 ** power
    assert board.stake_pow == power
    power = random.randint(0, 4)
    board.stake_pow = power
    assert board.stake == 2 ** power
    assert board.stake_pow == power


@pytest.mark.parametrize('bad', ['stake', None, object()])
def test_stake_setting_raises_type(bad):
    board = random.choice(BOARDS)
    with pytest.raises(TypeError):
        board.stake = bad


@pytest.mark.parametrize('bad', [-1, 0, -42, 3, 5, 6, 13])
def test_stake_setting_raises_value(bad):
    board = random.choice(BOARDS)
    with pytest.raises(ValueError):
        board.stake = bad


def test_board_hash():
    n_rand = 5
    hashes = set()
    for board in BOARDS + [rand_board() for _ in range(n_rand)]:
        h = hash(board)
        assert isinstance(h, int)
        hashes.add(h)
    assert len(hashes) > 0.8 * (len(BOARDS) + n_rand), "too many hash collisions"


@pytest.mark.parametrize('board', BOARDS)
def test_board_copy(board: Board):
    copy = board.copy()
    assert copy is not board
    assert copy == board


@pytest.mark.parametrize('board', BOARDS[1:])
def test_board_flipping(board: Board):
    flipped = board.copy()
    flipped.flip()
    assert flipped.turn.other() == board.turn
    assert flipped.doubling_turn.other() == board.doubling_turn
    assert flipped.stake == board.stake

    assert flipped.flipped() == board
    assert flipped.turn.other() == board.turn
    flipped.flip()
    assert flipped == board
