import pytest

from backgammon.core.move import Move


def test_move_str_repr():
    move = Move(17, 11)
    assert repr(move) == 'Move(17, 11)'
    assert str(move) == '17/11'

    move = Move(4, 6, True)
    assert repr(move) == 'Move(4, 6, hit=True)'
    assert str(move) == '4/6*'
    assert move.to_str(regular=True) == '21/19*'

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


def test_move_consistency_ckeck():
    # some regular game
    for src in [0, 1, 4, 8, 13, 19, 24, 25]:
        for pips in [-6, -5, -3, 1, 3, 6]:
            dst = src + pips
            if 0 <= dst <= 25:
                move = Move(src, dst)
                assert_consistent_data(move)
                assert move.pips == abs(pips)
                if dst not in (0, 25):
                    move = Move(src, dst, True)
                    assert not move.bearing_off
                    assert_consistent_data(move)
                else:
                    assert move.bearing_off

    # points may not be 'off the board' (where bar and 'off' are okay, though)
    for bad in [-5, -1, 26, 42]:
        for good in [0, 1, 7, 19, 25]:
            for hit in [False, True]:
                for src, dst in [(bad, good), (good, bad)]:
                    with pytest.raises(ValueError):
                        move = Move(src, dst, hit)
                        assert_consistent_data(move)

    # impossible to hit when bearing off
    for move in [Move(21, 25, True), Move(4, 0, True)]:
        with pytest.raises(ValueError):
            assert move.bearing_off
            assert_consistent_data(move)

    # wrong type should trough
    for move in [Move('21', 17), Move(4, None, True), Move(21, 0, 0)]:
        with pytest.raises(TypeError):
            assert_consistent_data(move)
