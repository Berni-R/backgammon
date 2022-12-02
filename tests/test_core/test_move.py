import pytest

from backgammon.core.move import Move
from backgammon.core.board import WHITE_BAR, BLACK_BAR


def test_move_str_repr():
    move = Move(17, 11)
    assert repr(move) == 'Move(17, 11)'
    assert str(move) == '17/11'

    move = Move(4, 6, True)
    assert repr(move) == 'Move(4, 6, hit=True)'
    assert str(move) == '21/19*'
    assert move.to_str(regular=False) == '4/6*'

    move = Move(25, 21, True)
    assert repr(move) == 'Move(25, 21, hit=True)'
    assert str(move) == 'bar/21*'

    move = Move(5, 0)
    assert repr(move) == 'Move(5, 0)'
    assert str(move) == '5/off'
    assert move.to_str(bar_off=False) == '5/0'


def assert_consistent_data(move: Move):
    if not isinstance(move.src, int):
        raise TypeError(f"`src` needs to be an integer, but is {move.src} ({type(move.src)}).")
    if not isinstance(move.dst, int):
        raise TypeError(f"`dst` needs to be an integer, but is {move.dst} ({type(move.dst)}.")
    if not isinstance(move.hit, bool):
        raise TypeError(f"`hit` needs to be a boolean value, but is {move.hit} ({type(move.hit)}).")

    if not 0 <= move.src <= 25:
        raise ValueError(f"`src` needs to be in [0, 25], but is {move.src}.")
    if not 0 <= move.dst <= 25:
        raise ValueError(f"`dst` needs to be in [0, 25], but is {move.dst}.")
    if move.hit and move.dst in (0, 25):
        raise ValueError("impossible to hit when bearing off")


@pytest.mark.parametrize('src', [0, 1, 4, 8, 13, 19, 24, 25])
@pytest.mark.parametrize('pips', [-6, -5, -3, 1, 3, 6])
def test_move_pips(src: int, pips: int):
    # some regular game
    dst = src + pips
    if 0 <= dst <= 25:
        move = Move(src, dst)
        assert_consistent_data(move)
        assert move.pips() == abs(pips)
        if dst in (BLACK_BAR, WHITE_BAR):
            assert move.bearing_off()
        else:
            move = Move(src, dst, True)
            assert not move.bearing_off()
            assert_consistent_data(move)


def test_move_hash():
    hashes = set()
    for src in range(26):
        for dst in range(26):
            for hit in (True, False):
                m = Move(src, dst, hit)
                hashes.add(hash(m))
    assert len(hashes) > 0.9 * 2 * 26**2
