from typing import Literal, Iterable
from svgwrite.drawing import Drawing  # type: ignore
from svgwrite import shapes, container  # type: ignore
from svgwrite.utils import strlist  # type: ignore
import numpy as np


class DrawingPlus(Drawing):

    def __init__(
            self,
            size: Iterable[float | int],
            origin: Iterable[float | int] = (0, 0),
            filename: str = "noname.svg",
            profile: str = "full",
            **extra
    ):
        size = tuple(size)
        origin = tuple(origin)
        if len(size) != 2 or not all(isinstance(s, (int, float)) for s in size):
            raise ValueError("`size` must be a 2-tuple of float or int")
        if len(origin) != 2 or not all(isinstance(s, (int, float)) for s in origin):
            raise ValueError("`origin` must be a 2-tuple of float or int")

        self.origin = origin

        super().__init__(filename=filename, size=size, profile=profile, **extra)

    def add(self, element):
        # left append the translation - a simple `element.translate` would mess with other transforms
        transforms = element.attribs.get(element.transformname, '')
        shift = "translate(%s)" % strlist(self.origin)
        element[element.transformname] = ("%s %s" % (shift, transforms)).strip()
        super().add(element)

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

    def die(self, center: tuple, n: int | str, size: float, fill: str, point_color: str = 'black',
            stroke_width: float = 1, font_family: str = 'Arial', rotate: float = 0.0) -> container.Group:
        x, y = center

        die = self.g()

        empty_die = self.rect((x-size/2, y-size/2), (size, size), rx=0.15*size, ry=0.15*size,
                              stroke="black", stroke_width=stroke_width, line_loc='inside', fill=fill)
        die.add(empty_die)

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
                point = self.circle((x + (xi-0.5) * size, y + (yi-0.5) * size), r=0.09 * size, fill=point_color)
                die.add(point)
        else:  # isinstance(n, str):
            text = self.text(n, (x, y), dominant_baseline="central", text_anchor="middle", font_size=0.65 * size,
                             font_family=font_family, fill=point_color)
            die.add(text)

        die.rotate(rotate, (x, y))

        return die
