import numpy as np
from matplotlib.colors import hex2color, rgb2hex  # type: ignore
from svgwrite import Drawing  # type: ignore
from PIL import Image  # type: ignore
from tempfile import NamedTemporaryFile  # type: ignore
from cairosvg import svg2png  # type: ignore


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


def svg2image(svg: Drawing, **kwargs) -> Image.Image:
    """Convert an SVG Drawing into a PIL Image.

    Args:
         svg (Drawing): The SVG to convert.
         **kwargs:      Keyword arguments are passed to `svg2png`. Most noteable, ther is
                        dpi: int = 96,
                        parent_width: Any = None,
                        parent_height: Any = None,
                        scale: int = 1,
                        output_width: Any = None,
                        output_height: Any = None,
    Retuns:
        image (PIL.Image.Image):    The converted image.
    """
    # TODO: is there a better method - this is relatively slow (~50ms)
    tmp_svg = NamedTemporaryFile('w+', encoding='utf-8')
    with open(tmp_svg.name, 'w', encoding='utf-8') as f:
        svg.write(f)

    tmp_png = NamedTemporaryFile()
    svg2png(url=tmp_svg.name, write_to=tmp_png.name, **kwargs)
    return Image.open(tmp_png.name)
