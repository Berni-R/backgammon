from typing import Iterable, Any
import numpy as np

from ..core import Color, Move, Board
from ..core import BLACK_BAR, WHITE_BAR, START_POINTS
from ..core import GameState
from .style import DisplayStyle
from .board_svg import BoardDrawing


def svg_board(
        board: Board,
        ds: DisplayStyle | None = None,
        dice: Iterable[int] | None = None,
        dice_colors: Iterable[str] | None = None,
        doubling_die: tuple[int, Color] | None = None,
        turn_marker: Color = Color.NONE,
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
        doubling_die=doubling_die, turn_marker=turn_marker,
        highlight_pnt=highlight_pnt, highlight_chk=highlight_chk,
        swap_ints=swap_ints, show_pips=show_pips,
    ))
    return drawing


def get_dice_colors(state: GameState, ds: DisplayStyle,
                    dice: list[int] | None = None, game_start: bool | None = None) -> list[str]:
    if dice is None:
        dice = state.dice
    if game_start is None:
        # theoretically, this situation is possible later in the game - it should be extremely rare, though
        game_start = bool(np.all(state.board.points == START_POINTS)) and state.stake == 1

    if game_start:
        if len(dice) == 2:
            dice_colors = [ds.chk_dark, ds.chk_light]
        else:
            dice_colors = ['gray'] * len(dice)
    else:
        dice_colors = [ds.chk_dark if state.turn == Color.BLACK else ds.chk_light] * len(dice)

    for i, used in enumerate(state.dice_used):
        if used:
            dice_colors[i] = 'gray'

    return dice_colors


def svg_gamestate(
        state: GameState,
        last_move: Move | None = None,
        ds: DisplayStyle | None = None,
        dice: list[int] | None = None,
        dice_colors: list[str] | None = None,
        doubling_die: tuple[int, Color] | None = None,
        turn_marker: Color = Color.NONE,
        highlight_pnt: Iterable[int] | dict[int, Any] | None = None,
        highlight_chk: Iterable[int | tuple[int, int]] | dict[int | tuple[int, int], Any] | None = None,
        swap_ints: bool | None = None,
        show_pips: bool = True,
) -> BoardDrawing:
    if ds is None:
        ds = DisplayStyle()

    if dice is None:
        dice = state.dice

    if dice_colors is None:
        dice_colors = get_dice_colors(state, dice=dice, ds=ds)

    if doubling_die is None:
        doubling_die = (state.stake, state.doubling_turn)
    if turn_marker is None:
        turn_marker = state.turn

    if last_move is not None:
        if highlight_chk is None:
            highlight_chk = {}
        if not isinstance(highlight_chk, dict):
            highlight_chk = {pnt: ds.highlight_color_1 for pnt in highlight_chk}

        highlight_chk[(last_move.src, abs(state.board.points[last_move.src]))] = ds.highlight_color_1
        if last_move.dst not in [BLACK_BAR, WHITE_BAR]:
            highlight_chk[last_move.dst] = ds.highlight_color_2 if last_move.hit else ds.highlight_color_1
        if last_move.hit:
            bar = WHITE_BAR if state.turn == Color.BLACK else BLACK_BAR
            highlight_chk[bar] = ds.highlight_color_2

    if swap_ints is None:
        swap_ints = state.turn == Color.BLACK

    drawing = BoardDrawing(ds)
    drawing.add(drawing.board(
        state.board,
        dice=dice,
        dice_colors=dice_colors,
        doubling_die=doubling_die,
        turn_marker=turn_marker,
        highlight_pnt=highlight_pnt,
        highlight_chk=highlight_chk,
        swap_ints=swap_ints,
        show_pips=show_pips
    ))

    return drawing
