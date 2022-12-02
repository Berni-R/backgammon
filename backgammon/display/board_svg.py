from typing import Any, Literal, Iterable
from svgwrite.drawing import Drawing  # type: ignore
from svgwrite import shapes, container, gradients  # type: ignore
from svgwrite.utils import strlist  # type: ignore
import numpy as np

from ..core import Color, Board
from .style import DisplayStyle
from .tools import brighten_color


class BoardDrawing(Drawing):

    def __init__(
            self,
            ds: DisplayStyle,
            size: tuple[float, float] | None = None,
            origin: tuple[float, float] | None = None,
            filename: str = "noname.svg",
            profile: str = "full",
            **extra
    ):
        if size is None:
            size = (
                ds.width + 2 * ds.boarder[0],
                ds.height + 2 * ds.boarder[1],
            )
        if origin is None:
            origin = tuple(ds.boarder)  # type: ignore

        self.ds = ds
        self.origin = origin

        super().__init__(filename=filename, size=size, profile=profile, **extra)
        self._def_checkers()

    def add(self, element):
        # left append the translation - a simple `element.translate` would mess with other transforms
        transforms = element.attribs.get(element.transformname, '')
        shift = "translate(%s)" % strlist(self.origin)
        element[element.transformname] = ("%s %s" % (shift, transforms)).strip()
        super().add(element)

    def _def_checkers(self):
        for color in (Color.BLACK, Color.WHITE):
            # for gradient see: https://www.w3.org/TR/SVG11/pservers.html#RadialGradientElementGradientUnitsAttribute
            grad_name = f"rad_grad_{color.name}"
            gradient = gradients.RadialGradient((0.5, 0.5), r=0.5, gradientUnits='objectBoundingBox', id=grad_name)
            c1 = self.ds.chk_light if color == Color.WHITE else self.ds.chk_dark
            c2 = brighten_color(c1, 0.9)
            c3 = brighten_color(c1, 0.5)
            gradient.add_stop_color(0.0, c1)
            gradient.add_stop_color(0.2, c1)
            gradient.add_stop_color(0.4, c2)
            gradient.add_stop_color(0.6, c1)
            gradient.add_stop_color(0.8, c1)
            gradient.add_stop_color(1.0, c3)
            self.defs.add(gradient)

            name = f"checker_{color.name}"
            checker = self.circle((0, 0), r=self.ds.scale/2, fill=f"url(#{grad_name})", id=name)
            self.defs.add(checker)

    def checker(self, center: Any, color: Color, **extra) -> container.Use:
        name = f"#checker_{color.name}"
        return self.use(name, center, **extra)

    def rect(self, insert: tuple, size: tuple,
             stroke_width: float = 0.0, line_loc: Literal['outside', 'inside', 'mid'] = 'mid', **extra) -> shapes.Rect:
        x, y = insert
        w, h = size

        if line_loc == 'outside':
            x = x - stroke_width / 2
            y = y - stroke_width / 2
            w += stroke_width
            h += stroke_width
        elif line_loc == 'inside':
            x = x + stroke_width / 2
            y = y + stroke_width / 2
            w -= stroke_width
            h -= stroke_width
        elif line_loc != 'mid':
            raise ValueError(f"Unknown line location '{line_loc}'")

        # these factory methods like Drawing.rect are not methods, but inherit the __getattr__ from ElementFactory...
        # ... in effect they, however, only add `factory=self`. Hence:
        extra['factory'] = self
        return shapes.Rect((x, y), (w, h), stroke_width=stroke_width, **extra)

    def die(self, center: tuple, n: int | str, fill: str | None = None, size: float | None = None,
            rotate: float = 0.0) -> container.Group:
        x, y = center
        if size is None:
            size = self.ds.die_size
        if fill is None:
            fill = self.ds.die_color

        die = self.g()

        empty_die = self.rect((x-size/2, y-size/2), (size, size), rx=0.15*size, ry=0.15*size,
                              stroke="black", stroke_width=self.ds.lw/2, line_loc='inside', fill=fill)
        die.add(empty_die)

        dark_color = "black"
        if isinstance(n, (int, np.int_)):
            pos: list[list[tuple[float, float]]] = [
                [],
                [(0.50, 0.50)],
                [(0.25, 0.25), (0.75, 0.75)],
                [(0.25, 0.25), (0.50, 0.50), (0.75, 0.75)],
                [(0.25, 0.25), (0.25, 0.75), (0.75, 0.75), (0.75, 0.25)],
                [(0.25, 0.25), (0.25, 0.75), (0.50, 0.50), (0.75, 0.75), (0.75, 0.25)],
                [(0.25, 0.25), (0.25, 0.50), (0.25, 0.75), (0.75, 0.75), (0.75, 0.50), (0.75, 0.25)],
            ]
            for xi, yi in pos[n]:
                point = self.circle((x + (xi-0.5) * size, y + (yi-0.5) * size), r=0.09 * size, fill=dark_color)
                die.add(point)
        else:  # isinstance(n, str):
            text = self.text(n, (x, y), dominant_baseline="central", text_anchor="middle",
                             font_size=0.65 * size, font_family=self.ds.font, fill=dark_color)
            die.add(text)

        die.rotate(rotate, (x, y))

        return die

    def dice(self, dice: list[int], dice_colors: list[str]) -> container.Group:
        if len(dice_colors) != len(dice):
            raise ValueError(f"length of dice colors ({len(dice_colors)}) does not match the dice ({len(dice)})")

        def rand():
            return 0.0  # 0.2 * (np.random.rand() - 0.5)

        ds = self.ds
        # TODO: centre the dice in the board
        off, dist = (1.0, 1.7) if len(dice) > 2 else (1.2, 2.2)
        g = self.g()
        for i, (d, c) in enumerate(zip(dice, dice_colors)):
            x = 0.5 * ds.width + ds.bar_width / 2 + ((off + i) * dist + rand()) * ds.die_size
            y = 0.5 * ds.height + 0.4 * rand() * ds.scale
            die = self.die((x, y), d, fill=c)  # , rotate=360 * np.random.rand())
            g.add(die)
        return g

    def hinge(self, insert: tuple, size: tuple | None = None, **extra) -> container.Group:
        if size is None:
            size = self.ds.hinge_size
        dark = "black"  # brighten_color(self.ds.metal_color, 0.5)
        x, y = insert
        width, height = size

        hinge = self.g()

        plate = self.rect(insert, size, fill=self.ds.metal_color,
                          stroke=dark, stroke_width=self.ds.lw / 2, line_loc='inside', **extra)
        hinge.add(plate)
        hinge.add(self.line(
            (x + width / 2, y),
            (x + width / 2, y + height),
            stroke=dark, stroke_width=self.ds.lw / 2),
        )

        for dx in (0.2, 0.8):
            for dy in (0.25, 0.75):
                rivet = self.circle((x + dx * width, y + dy * height), r=0.05 * self.ds.scale, fill=dark)
                hinge.add(rivet)

        return hinge

    def point_triangle(self, point: int, fill: str | None = None, **extra) -> shapes.Polygon:
        if fill is None:
            fill = self.ds.pnt_light if point % 2 == 1 else self.ds.pnt_dark
        x, up = self.ds.point_to_x_updown(point)
        y = int(up) * self.ds.height
        d = (-1 if up else 1)
        return self.polygon([(x - self.ds.scale / 2, y),
                             (x, y + d * self.ds.point_height),
                             (x + self.ds.scale / 2, y)], fill=fill, **extra)

    def point_text(self, point: int, text: str, fill: str = "black", **extra) -> shapes.Polygon:
        x, up = self.ds.point_to_x_updown(point)
        y = int(up) * self.ds.height
        d = (-1 if up else 1)
        return self.text(text, (x, y - d * 0.4 * self.ds.boarder[1]),
                         dominant_baseline="central", text_anchor="middle",
                         font_size=0.3 * self.ds.scale, font_family=self.ds.font, fill=fill, **extra)

    def empty_board(self, flip_points: bool = False) -> container.Group:
        ds = self.ds

        board = self.g()

        r = self.rect((-ds.boarder[0], -ds.boarder[1]), (ds.width + 2 * ds.boarder[0], ds.height + 2 * ds.boarder[1]),
                      fill=ds.bg_dark, stroke="black", stroke_width=ds.lw, line_loc="inside")
        board.add(r)

        field = self.rect((0, 0), (ds.width, ds.height), fill=ds.bg_light, stroke="black", stroke_width=ds.lw,
                          line_loc="outside")
        board.add(field)
        bar = self.rect((6 * ds.point_width, -ds.lw), (ds.bar_width, ds.height + 2 * ds.lw), fill=ds.bg_dark,
                        stroke="black", stroke_width=ds.lw, line_loc="inside")
        board.add(bar)
        board.add(self.line(
            (ds.width / 2, -ds.boarder[1]),
            (ds.width / 2, ds.height + 2 * ds.boarder[1]),
            stroke='black', stroke_width=ds.lw / 2),
        )

        width, height = self.ds.hinge_size
        board.add(self.hinge((ds.width / 2 - width / 2, 0.25 * ds.height - height / 2)))
        board.add(self.hinge((ds.width / 2 - width / 2, 0.75 * ds.height - height / 2)))

        slot_height = 15 * ds.checkers_height
        for side in ('left', 'right'):
            for up in (False, True):
                slot = self.rect(ds.slot_pos(side, up), (ds.scale, slot_height), fill=ds.bg_light,
                                 stroke="black", stroke_width=ds.lw, line_loc='outside')
                board.add(slot)

        for pnt in range(1, 24+1):
            triangle = self.point_triangle(pnt)
            board.add(triangle)

            point = 25 - pnt if flip_points else pnt
            text = self.point_text(pnt, f"{point}")
            board.add(text)

        return board

    def all_checkers(self, board: Board) -> container.Group:
        ds = self.ds
        checkers = self.g()

        # checkers on points & bar
        for pnt in range(len(board.points)):
            color = board.color_at(pnt)
            for n in range(abs(board.points[pnt])):
                xy = ds.checker_pos(pnt, n)
                checkers.add(self.checker(xy, color))

        # borne off checkers
        for color in (Color.BLACK, Color.WHITE):
            off = max(0, 15 - board.checkers_count(color))
            if color == Color.WHITE:
                c = ds.chk_light
                y = ds.height - ds.checkers_height
            else:
                c = ds.chk_dark
                y = 0
            x, _ = ds.slot_pos('right', up=(color == Color.BLACK))
            for n in range(off):
                r = self.rect((x, y - color * n * ds.checkers_height),
                              (ds.scale, ds.checkers_height),
                              fill=c, stroke=brighten_color(c, 0.5), stroke_width=ds.lw/2, line_loc='inside')
                checkers.add(r)

        return checkers

    def board(
            self,
            board: Board,
            dice: Iterable[int] | None = None,
            dice_colors: Iterable[str] | None = None,
            highlight_pnt: Iterable[int] | dict[int, Any] | None = None,
            highlight_chk: Iterable[int | tuple[int, int]] | dict[int | tuple[int, int], Any] | None = None,
            swap_ints: bool = True,
            show_pips: bool = True,
    ) -> container.Group:
        # TODO: highlight borne off checkers
        ds = self.ds
        b = self.g()

        # background / board
        b.add(self.empty_board(flip_points=swap_ints and board.turn == Color.BLACK))

        # highlight points
        if highlight_pnt is not None:
            if not isinstance(highlight_pnt, dict):
                highlight_pnt = {pnt: ds.highlight_color_1 for pnt in highlight_pnt}
            for pnt, color in highlight_pnt.items():
                if not 1 <= pnt <= 24:
                    raise ValueError(f"{pnt} is not a point on the board that can be highlighted")
                # TODO: draw line inside the triangle
                b.add(self.point_triangle(pnt, fill='none', stroke=color, stroke_width=ds.lw))

        # turn marker
        if board.turn != Color.NONE:
            b.add(self.circle(**ds.turn_marker_attrs(board.turn)))

        # doubling die
        if board.stake != 1 and board.doubling_turn != Color.NONE:
            b.add(self.die(ds.doubling_die_pos(board.doubling_turn), str(board.stake)))

        # checkers
        b.add(self.all_checkers(board))

        # highlight checkers
        if highlight_chk is not None:
            if not isinstance(highlight_chk, dict):
                highlight_chk = {pnt: ds.highlight_color_1 for pnt in highlight_chk}
            for pnt, color in highlight_chk.items():
                if isinstance(pnt, tuple):
                    pnt, n = pnt
                else:
                    n = max(0, abs(board.points[pnt])-1)
                xy = ds.checker_pos(pnt, n)
                b.add(self.circle(xy, r=ds.scale/2-ds.lw/2, fill='none', stroke=color, stroke_width=ds.lw))

        # pip count
        if show_pips:
            for color in (Color.BLACK, Color.WHITE):
                attrs = ds.pip_text_attrs(color)
                b.add(self.text(f"{board.pip_count(color)}", **attrs))

        # dice
        if dice is not None:
            dice = list(dice)
            if dice_colors is None:
                if board.turn is Color.BLACK:
                    dice_colors = [ds.chk_dark] * len(dice)
                elif board.turn is Color.WHITE:
                    dice_colors = [ds.chk_light] * len(dice)
                else:
                    raise ValueError("Need to specify dice colors (no turn given)")
            dice_colors = list(dice_colors)

            b.add(self.dice(dice, dice_colors))

        return b
