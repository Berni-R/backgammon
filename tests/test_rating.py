import numpy as np

from backgammon.rating import FIBSRating, INITIAL_RATING


def test_rating():
    for r1, r2 in [(1500.0, 1800.0), (1234.5, 1325.4), (1400, 1300)]:
        for ramp_up in [True, False]:
            r1 = FIBSRating(r1, ramp_up=ramp_up)
            r2 = FIBSRating(r2, ramp_up=ramp_up)

            for length in [1, 2, 3, 5, 11]:
                assert np.allclose(r1.win_prob(r2, length), 1.0 - r2.win_prob(r1, length))
                d = FIBSRating.mutual_update(winner=r1, looser=r2, match_len=length)
                assert d[0] == -d[1]


def test_rating_stats():
    for win_prob in [0.2, 0.5, 0.6]:
        r = FIBSRating()
        ref = FIBSRating(fixed=True)
        for _ in range(3000):  # ramp up is 400 points
            win = np.random.rand() < win_prob
            winner, looser = (r, ref) if win else (ref, r)
            FIBSRating.mutual_update(winner, looser, match_len=1)
        assert ref == INITIAL_RATING  # it is fixed!
        assert np.allclose(r.win_prob(ref, match_len=1), win_prob, rtol=0.05, atol=0.02)
        assert np.allclose(r - ref, FIBSRating.diff_for_win_prob(win_prob, match_len=1), rtol=0.1, atol=30.0)
