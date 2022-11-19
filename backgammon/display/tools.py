from typing import Literal
import numpy as np
import drawSvg as draw  # type: ignore
from matplotlib.colors import hex2color, rgb2hex  # type: ignore


def staple_pos(pos: int, max_n: int) -> float:
    pos = min(max_n * (max_n + 1) // 2 - 1, pos)
    sub = max_n
    off = 0.5
    while pos >= sub:
        pos = pos - sub
        sub -= 1
        off += 0.5
    return pos + off


def brighten_color(color_hex: str, factor: float) -> str:
    return rgb2hex(np.clip(np.array(hex2color(color_hex)) * factor, 0, 1))


def rect(x: float, y: float, w: float, h: float,
         stroke_width: float = 0.0, line_loc: Literal['outside', 'inside', 'mid'] = 'mid', **kwargs):
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
    return draw.Rectangle(x, y, w, h, stroke_width=stroke_width, **kwargs)
