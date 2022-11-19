import drawSvg as draw  # type: ignore

from ..core import Color
from ..board import Board
from .style import DisplayStyle
from .tools import staple_pos, brighten_color, rect


def get_canvas(ds: DisplayStyle) -> draw.Drawing:
    return draw.Drawing(
        ds.width + 2 * ds.boarder[0],
        ds.height + 2 * ds.boarder[1],
        origin=(-ds.boarder[0], -ds.boarder[1]),
        displayInline=False,
    )


def draw_board(ds: DisplayStyle, flip_points: bool = False) -> draw.Group:
    board = draw.Group()

    board.append(rect(-ds.boarder[0], -ds.boarder[1], ds.width + 2 * ds.boarder[0], ds.height + 2 * ds.boarder[1],
                      fill=ds.bg_dark, stroke="black", stroke_width=ds.lw, line_loc="inside"))

    field = rect(0, 0, ds.width, ds.height, fill=ds.bg_light, stroke="black", stroke_width=ds.lw, line_loc="outside")
    bar = rect(6 * ds.point_width, -ds.lw, ds.bar_width, ds.height + 2 * ds.lw, fill=ds.bg_dark,
               stroke="black", stroke_width=ds.lw, line_loc="inside")
    board.append(field)
    board.append(bar)

    def add_hinge(h):
        height = 1.2 * ds.scale
        width = 2 / 3 * ds.scale
        hinge = rect(ds.width / 2 - ds.scale / 3, h * ds.height - height / 2, width, height,
                     fill=ds.metal_color, stroke="black", stroke_width=ds.lw / 2)
        board.append(hinge)
        for x_off in (-0.2, 0.2):
            for y_off in (-0.25, 0.25):
                rivet = draw.Circle(ds.width / 2 + x_off * ds.scale, h * ds.height + y_off * height, 0.05 * ds.scale)
                board.append(rivet)
    add_hinge(0.25)
    add_hinge(0.75)

    board.append(draw.Line(ds.width / 2, -ds.boarder[1],
                          ds.width / 2, ds.height + 2 * ds.boarder[1], stroke='black', stroke_width=ds.lw / 2))

    slot_height = 15 * ds.checkers_height
    for side in ('left', 'right'):
        x = ds.width + ds.boarder[0] / 2 - ds.scale / 2 if side == 'right' else -ds.boarder[0] / 2 - ds.scale / 2
        for up in (False, True):
            y = 0 if up else ds.height - slot_height
            slot = rect(x, y, ds.scale, slot_height,
                        fill=ds.bg_light, stroke="black", stroke_width=ds.lw, line_loc='outside')
            board.append(slot)

    def draw_point(point):
        x, up = ds.point_to_x_updown(point)
        y = int(up) * ds.height
        d = (-1 if up else 1)
        fill = ds.pnt_light if point % 2 == 1 else ds.pnt_dark
        triangle = draw.Lines(x - ds.scale / 2, y,
                              x, y + d * ds.point_height,
                              x + ds.scale / 2, y, fill=fill)
        board.append(triangle)

        if flip_points:
            point = 25 - point
        text = draw.Text(f"{point}", x=x, y=y - d * 0.4 * ds.boarder[1],
                         text_anchor='middle', valign='middle',
                         fontSize=0.3 * ds.scale, fontFamily=ds.font, fill='black')
        board.append(text)

    for pnt in range(1, 24+1):
        draw_point(pnt)

    return board


def draw_checker(x: float, y: float, color: Color, ds: DisplayStyle, id: str | None = None) -> draw.Circle:
    # for gradient see: https://www.w3.org/TR/SVG11/pservers.html#RadialGradientElementGradientUnitsAttribute
    gradient = draw.RadialGradient(0.5, 0.5, 0.5, gradientUnits='objectBoundingBox')
    c1 = ds.chk_light if color == Color.WHITE else ds.chk_dark
    c2 = brighten_color(c1, 0.9)
    c3 = brighten_color(c1, 0.5)
    gradient.addStop(0.0, c1)
    gradient.addStop(0.2, c1)
    gradient.addStop(0.4, c2)
    gradient.addStop(0.6, c1)
    gradient.addStop(0.8, c1)
    gradient.addStop(1.0, c3)

    args = {}
    if id is not None:
        args['id'] = id
    return draw.Circle(x, y, ds.scale/2, fill=gradient, **args)


def draw_checkers(pnt: int, n: int, color: Color, canv: draw.Drawing, ds: DisplayStyle):
    x, up = ds.point_to_x_updown(pnt)
    for pos in range(n):
        y = staple_pos(pos, 5) * ds.scale
        if up:
            y = ds.height - y
        canv.append(draw_checker(x, y, color, ds))


def draw_die(x: float, y: float, n: int | str, ds: DisplayStyle, fill: str | None = None,
             s: float | None = None) -> draw.Group:
    if fill is None:
        fill = ds.die_color
    if s is None:
        s = ds.die_size

    die = draw.Group()
    die.append(draw.Rectangle(x - 0.5 * s, y - 0.4 * s, s, 0.8 * s, fill=fill))
    die.append(draw.Rectangle(x - 0.4 * s, y - 0.5 * s, 0.8 * s, s, fill=fill))

    args = dict(stroke='black', stroke_width=ds.lw/2, fill=fill)
    die.append(draw.ArcLine(x - 0.4 * s, y - 0.4 * s, 0.1 * s, 180, 270, **args))
    die.append(draw.ArcLine(x - 0.4 * s, y + 0.4 * s, 0.1 * s, 90, 180, **args))
    die.append(draw.ArcLine(x + 0.4 * s, y + 0.4 * s, 0.1 * s, 0, 90, **args))
    die.append(draw.ArcLine(x + 0.4 * s, y - 0.4 * s, 0.1 * s, 270, 0, **args))

    del args['fill']
    die.append(draw.Line(x - 0.5 * s, y - 0.4 * s, x - 0.5 * s, y + 0.4 * s, **args))
    die.append(draw.Line(x - 0.4 * s, y + 0.5 * s, x + 0.4 * s, y + 0.5 * s, **args))
    die.append(draw.Line(x + 0.5 * s, y - 0.4 * s, x + 0.5 * s, y + 0.4 * s, **args))
    die.append(draw.Line(x - 0.4 * s, y - 0.5 * s, x + 0.4 * s, y - 0.5 * s, **args))

    if isinstance(n, str):
        text = draw.Text(n, x=x, y=y, text_anchor='middle', valign='middle',
                         fontSize=0.7 * s, fontFamily=ds.font, fill='black')
        die.append(text)
    else:
        raise NotImplementedError()

    return die


def board_svg(board: Board, ds: DisplayStyle | None = None, swap_ints: bool = True) -> draw.Drawing:
    if ds is None:
        ds = DisplayStyle()
    canv = get_canvas(ds)

    # background / board
    canv.append(draw_board(ds, flip_points=swap_ints and board.turn == Color.BLACK))

    # turn marker
    if board.turn == Color.WHITE:
        fill = ds.chk_light
        y = -ds.boarder[1] / 2
    elif board.turn == Color.BLACK:
        fill = ds.chk_dark
        y = ds.height + ds.boarder[1] / 2
    else:
        fill = 'gray'
        y = ds.height / 2

    if board.turn != Color.NONE:
        turn_marker = draw.Circle(ds.width + ds.boarder[0] - 0.3 * ds.scale, y, 0.15 * ds.scale, fill=fill)
        canv.append(turn_marker)

    # doubling die
    x, y = ds.width/2, ds.height/2
    if board.doubling_turn is Color.WHITE:
        y = ds.scale / 2
    elif board.doubling_turn is Color.BLACK:
        y = ds.height - ds.scale / 2
    if board.stake != 1 and board.doubling_turn is not None:
        die = draw_die(x, y, str(board.stake), ds)
        canv.append(die)

    # checkers on points
    for pnt in range(1, 24+1):
        color = board.color_at(pnt)
        draw_checkers(pnt, abs(board.points[pnt]), color, canv, ds)
    # checkers on bar
    x = ds.width / 2
    for i in range(abs(board.points[0])):
        y = ds.height / 2 - ds.point_space / 2 - staple_pos(i, 4) * ds.scale
        canv.append(draw_checker(x, y, Color.BLACK, ds))
    for i in range(abs(board.points[-1])):
        y = ds.height / 2 + ds.point_space / 2 + staple_pos(i, 4) * ds.scale
        canv.append(draw_checker(x, y, Color.WHITE, ds))
    # borne off checkers
    for color in (Color.BLACK, Color.WHITE):
        off = max(0, 15 - board.checkers_count(color))
        c = ds.chk_light if color == Color.WHITE else ds.chk_dark
        x = ds.width + ds.boarder[0] / 2 - ds.scale / 2
        y = 0 if color == Color.WHITE else ds.height - ds.checkers_height
        for n in range(off):
            r = rect(x, y + color * n * ds.checkers_height,
                     ds.scale, ds.checkers_height,
                     fill=c, stroke=brighten_color(c, 0.5), stroke_width=ds.lw / 2, line_loc='inside')
            canv.append(r)

    return canv
