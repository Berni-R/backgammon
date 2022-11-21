import numpy as np
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
