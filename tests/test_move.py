import pytest

from backgammon.moves.move import Move


def test_move_str_repr():
    move = Move(17, 11)
    assert repr(move) == 'Move(17, 11)'
    assert str(move) == '17/11'

    move = Move(4, 6, True)
    assert repr(move) == 'Move(4, 6, hit=True)'
    assert str(move) == '21/19*'

    move = Move(25, 21, True)
    assert repr(move) == 'Move(25, 21, hit=True)'
    assert str(move) == 'bar/21*'

    move = Move(5, 0)
    assert repr(move) == 'Move(5, 0)'
    assert str(move) == '5/off'
    assert move.to_str(bar_off=False) == '5/0'


def test_move_consistency_ckeck():
    # some regular moves
    for src in [0, 1, 4, 8, 13, 19, 24, 25]:
        for pips in [-6, -5, -3, 1, 3, 6]:
            dst = src + pips
            if 0 <= dst <= 25:
                move = Move(src, dst)
                move.assert_consistent_data()
                assert move.pips == abs(pips)
                if dst not in (0, 25):
                    move = Move(src, dst, True)
                    assert not move.bearing_off
                    move.assert_consistent_data()
                else:
                    assert move.bearing_off

    # points may not be 'off the board' (where bar and 'off' are okay, though)
    for bad in [-5, -1, 26, 42]:
        for good in [0, 1, 7, 19, 25]:
            for hit in [False, True]:
                for src, dst in [(bad, good), (good, bad)]:
                    with pytest.raises(ValueError):
                        move = Move(src, dst, hit)
                        move.assert_consistent_data()

    # impossible to hit when bearing off
    for move in [Move(21, 25, True), Move(4, 0, True)]:
        with pytest.raises(ValueError):
            assert move.bearing_off
            move.assert_consistent_data()

    # wrong type should trough
    for move in [Move('21', 17), Move(4, None, True), Move(21, 0, 0)]:
        with pytest.raises(TypeError):
            move.assert_consistent_data()
