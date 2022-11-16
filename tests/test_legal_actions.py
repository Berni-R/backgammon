import pytest
import numpy as np

from backgammon.core import Color
from backgammon.moves.move import Move
from backgammon.board import Board
from backgammon.actions import Doubling, Action, build_legal_actions, do_action, undo_action, is_legal_action


def test_build_legal_actions():
    board = Board()
    with pytest.raises(ValueError):
        build_legal_actions(board, [3, 5])

    board = Board(
        points=[0, -1, 1, 2, 1, 0, -1, 0, 0, -1, 0, 0, 0, 1, -1, 0, 0, 0, -1, 0, -1, 0, 0, 0, 1, 0],
        turn=Color.WHITE,
    )
    actions = build_legal_actions(board, [6, 2])
    assert set(actions) == {
        Action([Move(13, 7), Move(3, 1, hit=True)]),
        Action([Move(13, 7), Move(4, 2)]),
        Action([Move(13, 7), Move(7, 5)]),
        Action([Move(24, 18, hit=True), Move(13, 11)]),
        Action([Move(24, 18, hit=True), Move(18, 16)]),
        Action([Move(24, 18, hit=True), Move(3, 1, hit=True)]),
        Action([Move(24, 18, hit=True), Move(4, 2)]),
        Action([Move(24, 22), Move(13, 7)]),
        Action([Move(24, 22), Move(22, 16)]),
    }

    board = Board(
        points=[-1, -1, 2, 0, 0, 0, 6, 0, 0, 0, 0, 1, -4, 5, 0, 0, 0, -2, 0, -4, 0, -3, 1, 0, 0, 0],
        turn=Color.BLACK,
    )
    actions = build_legal_actions(board, [6, 2])
    assert actions == [Action([])]

    board = Board(
        points=[0, 1, -2, 1, 2, -1, 0, -3, -2, 0, 1, -1, 3, 0, 1, 2, -1, 0, -1, 0, 1, -1, -1, -1, 1, 1],
        turn=Color.BLACK,
    )
    actions = build_legal_actions(board, [1, 2])
    assert len(actions) == 72
    assert Action([Move(5, 6), Move(8, 10, hit=True)]) in actions
    assert Action([Move(5, 7), Move(18, 19)]) in actions
    assert Action([Move(25, 24), Move(20, 18, hit=True)]) not in actions
    assert Action([], Doubling.DOUBLE) not in actions
    assert Action([], Doubling.TAKE) not in actions

    board = Board(
        points=[-1, 1, 1, -2, -1, -1, 1, 1, 2, 0, 1, -2, 1, -2, 1, 0, -2, 2, -2, 0, 3, -1, -1, 1, 0, 0],
        turn=Color.BLACK,
        stake_pow=2,
        doubling_turn=Color.BLACK,
    )
    actions = build_legal_actions(board, [4, 4])
    assert len(actions) == 25
    for action in [
            Action([Move(0, 4), Move(3, 7, hit=True), Move(5, 9), Move(9, 13)]),
            Action([Move(0, 4), Move(3, 7, hit=True), Move(11, 15), Move(15, 19)]),
            Action([Move(0, 4), Move(5, 9), Move(11, 15), Move(18, 22)]),
            Action([Move(0, 4), Move(5, 9), Move(18, 22), Move(18, 22)]),
            Action([Move(0, 4), Move(11, 15), Move(15, 19), Move(19, 23, hit=True)]),
    ]:
        assert action in actions
    assert Action([Move(5, 9), Move(9, 13), Move(11, 15), Move(11, 15)]) not in actions

    for color in [Color.BLACK, Color.WHITE]:
        board = Board(
            points=[0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0],
            turn=color,
        )
        actions = build_legal_actions(board, [5, 2])
        assert set(actions) == {Action([Move(1, 0)])} or set(actions) == {Action([Move(24, 25)])}

    board = Board(
        points=[0, -2, 1, 2, 0, -3, -1, 0, 0, -1, 0, 0, 0, 1, -1, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0],
        turn=Color.BLACK,
    )
    actions = build_legal_actions(board, [2, 2])
    assert len(actions) == 120

    board = Board(
        points=[0, -2, 1, 2, 0, -3, -1, 0, 0, -1, 0, 0, 0, 1, -1, 0, 0, 0, -1, 0, -1, 0, 0, 0, 0, 0],
        turn=Color.WHITE,
    )
    actions = build_legal_actions(board, [6, 2])
    assert set(actions) == {Action([Move(13, 7)]), Action([Move(13, 11)])}


def test_do_undo_actions():
    def check_action(board_: Board, action_: Action):
        b = board_.copy()
        do_action(board_, action_)
        assert b.turn != board_.turn
        if action_.doubling == Doubling.TAKE:
            assert b.doubling_turn != board_.doubling_turn
        elif not action_.dances:
            assert np.any(b.points != board_.points)
        undo_action(board_, action_)
        assert b == board_

    board = Board()
    board.turn = Color.WHITE
    for action in [Action([]), Action([Move(8, 5), Move(6, 5)]), Action([], Doubling.DOUBLE),
                   Action([], Doubling.TAKE)]:
        assert is_legal_action(action, board)
        check_action(board, action)

    board = Board(
        points=[-2, 0, 0, 1, 1, 1, 1, 1, 0, 0, -2, -1, 3, 0, 0, 2, -1, -3, -2, 1, 2, 0, 0, 0, -1, 1],
        turn=Color.BLACK,
        stake_pow=3,
        doubling_turn=Color.BLACK,
    )
    for action in [Action([]), Action([Move(0, 6, hit=True), Move(0, 1)]), Action([], Doubling.DOUBLE)]:
        assert is_legal_action(action, board)
        check_action(board, action)
    board.doubling_turn = Color.WHITE
    for action in [Action([], Doubling.TAKE)]:
        assert is_legal_action(action, board)
        check_action(board, action)
