from backgammon.core.defs import Color, WinType, IllegalMoveError, ImpossibleMoveError, GameResult


def test_color_values():
    assert Color.NONE == 0
    assert Color.BLACK * Color.WHITE == -1
    assert abs(Color.BLACK) == 1
    assert abs(Color.WHITE) == 1


def test_color_other():
    assert Color.BLACK.other() == Color.WHITE
    assert Color.WHITE.other() == Color.BLACK

    assert Color.NONE.other() == Color.NONE


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
