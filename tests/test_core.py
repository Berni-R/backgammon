import random
from backgammon.core import Color, roll_dice, WinType, IllegalMoveError, ImpossibleMoveError, GameResult


def test_color():
    assert Color.BLACK.value == -1
    assert Color.NONE.value == 0
    assert Color.WHITE.value == 1

    assert Color.BLACK.other() == Color.WHITE
    assert Color.WHITE.other() == Color.BLACK

    assert Color.NONE.other() == Color.NONE


def test_roll_dice():
    for _ in range(1000):
        n = random.randint(1, 10)
        dice = roll_dice(n)
        assert len(dice) == n
        assert all(1 <= d <= 6 for d in dice)


def test_move_exceptions():
    assert isinstance(IllegalMoveError(), Exception)
    assert isinstance(ImpossibleMoveError(), IllegalMoveError)


def test_game_results():
    for i in range(6):
        res = GameResult(doubling_cube=2**i)
        assert res.stake == 2**i

        res = GameResult(doubling_cube=2**i, wintype=WinType.GAMMON)
        assert res.stake == 2 * 2**i

        res = GameResult(doubling_cube=2**i, wintype=WinType.BACKGAMMON)
        assert res.stake == 3 * 2**i
