import random

import pytest

from backgammon.core.defs import Color
from backgammon.core.move import Move
from backgammon.core.board import Board
from backgammon.core.legal_moves import build_legal_moves, is_legal_move
from .defs import BOARDS, BOARDS_N_MOVES


@pytest.mark.parametrize('board, n_moves_expected', zip(BOARDS, BOARDS_N_MOVES))
def test_moves_for_boards(board: Board, n_moves_expected: tuple[list[int], list[int]]):
    for color, moves_per_n in zip([Color.BLACK, Color.WHITE], n_moves_expected):
        for n, n_moves in enumerate(moves_per_n, start=1):
            legal_moves = build_legal_moves(board, pips=n, color=color)
            assert n_moves == len(legal_moves)
            for move in legal_moves:
                assert is_legal_move(move, board, color)


@pytest.mark.parametrize('board', BOARDS)
def test_non_legal_moves_for_boards(board: Board):
    legal_moves: list[Move] = sum(
        (
            build_legal_moves(board, pips=n, color=color)
            for n in range(1, 7)
            for color in (Color.BLACK, Color.WHITE)
        ),
        start=[],
    )

    for _ in range(100):
        src = random.randint(-2, 28)
        dst = random.randint(-2, 28)
        hit = random.choice([True, False])
        move = Move(src, dst, hit)
        try:
            color = board.color_at(src)
        except IndexError:
            color = Color.NONE

        if move in legal_moves:
            assert is_legal_move(move, board, color)
        else:
            if 1 <= move.pips() <= 6:
                assert not is_legal_move(move, board, color)
