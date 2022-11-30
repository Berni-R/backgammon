from typing import Iterable, Any
import numpy as np

from ..core import Color, _BLACK_BAR, _WHITE_BAR, _START_POINTS
from ..moves import Move
from ..board import Board
from ..game import GameState
from .style import DisplayStyle
from .board_svg import BoardDrawing


def svg_board(
        board: Board,
        ds: DisplayStyle | None = None,
        dice: Iterable[int] | None = None,
        dice_colors: Iterable[str] | None = None,
        highlight_pnt: Iterable[int] | dict[int, Any] | None = None,
        highlight_chk: Iterable[int | tuple[int, int]] | dict[int | tuple[int, int], Any] | None = None,
        swap_ints: bool = False,
        show_pips: bool = True,
) -> BoardDrawing:
    if ds is None:
        ds = DisplayStyle()

    drawing = BoardDrawing(ds)
    drawing.add(drawing.board(
        board,
        dice=dice, dice_colors=dice_colors,
        highlight_pnt=highlight_pnt, highlight_chk=highlight_chk,
        swap_ints=swap_ints, show_pips=show_pips,
    ))
    return drawing


def get_dice_colors(dice: list[int], game_start: bool, state: GameState, ds: DisplayStyle) -> list[str]:
    if game_start:
        if len(dice) == 2:
            dice_colors = [ds.chk_dark, ds.chk_light]
        else:
            dice_colors = ['gray'] * len(dice)
    else:
        dice_colors = [ds.chk_dark if state.board.turn == Color.BLACK else ds.chk_light] * len(dice)
    for i, unused in enumerate(state.dice_unused):
        if not unused:
            dice_colors[i] = 'gray'
    return dice_colors


def svg_gamestate(
        state: GameState,
        last_move: Move | None = None,
        ds: DisplayStyle | None = None,
        dice: Iterable[int] | None = None,
        dice_colors: Iterable[str] | None = None,
        highlight_pnt: Iterable[int] | dict[int, Any] | None = None,
        highlight_chk: Iterable[int | tuple[int, int]] | dict[int | tuple[int, int], Any] | None = None,
        swap_ints: bool = False,
        show_pips: bool = True,
) -> BoardDrawing:
    if ds is None:
        ds = DisplayStyle()

    drawing = BoardDrawing(ds)

    if dice is None:
        dice = state.dice

    if dice_colors is None:
        # theoretically, this situation is possible later in the game - it should be extremely rare, though
        game_start = np.all(state.board.points == _START_POINTS)
        dice_colors = get_dice_colors(dice, game_start=game_start, state=state, ds=ds)

    if last_move is not None:
        if highlight_chk is None:
            highlight_chk = {}
        highlight_chk[(last_move.src, abs(state.board.points[last_move.src]))] = ds.highlight_color_1
        if last_move.dst not in [_BLACK_BAR, _WHITE_BAR]:
            highlight_chk[last_move.dst] = ds.highlight_color_2 if last_move.hit else ds.highlight_color_1
        if last_move.hit:
            bar = _WHITE_BAR if state.board.turn == Color.BLACK else _BLACK_BAR
            highlight_chk[bar] = ds.highlight_color_2

    drawing.add(drawing.board(
        state.board,
        dice=dice, dice_colors=dice_colors,
        highlight_pnt=highlight_pnt, highlight_chk=highlight_chk,
        swap_ints=swap_ints, show_pips=show_pips,
    ))

    return drawing
