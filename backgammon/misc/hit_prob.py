import numpy as np

from backgammon.core import Color, Board, BLACK_BAR, WHITE_BAR


def hit_prob(board: Board, point: int, by: Color | None = None, only_legal: bool = False) -> float:
    """Calculate the probability by which the given point can be hit in the next move, given it is legal.

    Args:
        board (Board):      The board on which / the board for which to calculate the hitting probabilities.
        point (int):        The point in question of being hit. This can be any point, also empty ones and those of
                            the same color as `by`.
        by (Color):         By which color the point might be hit. If it is None, it defaults to the opposing color
                            of which the board on the given `point` are.
        only_legal (bool):  Restrict to legals game. This means, that if there are board of the hitter's color
                            on the bar, only considers those as potential hitters, ignore all other board.

    Returns:
        p (float):          The probabilty by which the given point could be hit in the next move.
    """
    if not 0 <= point <= 25:
        raise IndexError(f"{point} is not a valid point to hit")
    if point in (BLACK_BAR, WHITE_BAR):
        return 0.0
    if by is None:
        by = board.color_at(point).other()
    if by is Color.NONE:
        raise ValueError("Color by which to hit is undefined.")
    # assert by is not None
    by_i = int(by)

    def is_not_blocked(dist: int) -> bool:
        return 0 <= point + by_i * dist <= 25 and by_i * board.points[point + by_i * dist] >= -1

    if only_legal and by == Color.BLACK and board.points[BLACK_BAR] < 0:
        hitters_at = np.array([BLACK_BAR])
    elif only_legal and by == Color.WHITE and board.points[WHITE_BAR] > 0:
        hitters_at = np.array([WHITE_BAR])
    else:
        hitters_at = np.where(np.sign(board.points) == by_i)[0]

    dists = by_i * (hitters_at - point)
    options = 0
    for d1 in range(1, 6 + 1):
        if d1 in dists:
            options += 6
            continue
        for d2 in range(1, 6 + 1):
            if d2 in dists:
                options += 1
            else:
                if d1 == d2:
                    mid = d1
                    d = 2 * d1
                    while d < 5 * d1:
                        if is_not_blocked(mid):
                            if d in dists:
                                options += 1
                                break  # no multi-count of other potential possibilities
                        else:
                            break  # in-between point is blocked - cannot walk further anyway
                        mid += d1
                        d += d1
                elif d1 + d2 in dists:  # not a double roll
                    if is_not_blocked(d1) or is_not_blocked(d2):
                        options += 1

    return options / 36
