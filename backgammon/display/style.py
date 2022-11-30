from typing import Any

from ..core import Color
from .tools import staple_pos


class DisplayStyle:

    def __init__(
            self,
            scale: float = 30,
            boarder: tuple[float, float] = (1.8, 0.67),
            lw: float = 1/15,
            chk_light: str = f"#{255:x}{215:x}{130:x}",
            chk_dark: str = f"#{150:x}{50:x}{20:x}",
            pnt_light: str = f"#{160:x}{120:x}{65:x}",
            pnt_dark: str = f"#{100:x}{75:x}{42:x}",
            bg_light: str = f"#{200:x}{155:x}{85:x}",
            bg_dark: str = f"#{185:x}{135:x}{70:x}",
            metal_color: str = f"#{170:x}{174:x}{190:x}",
            die_color: str = f"#{225:x}{225:x}{225:x}",
            highlight_color_1: str = "lime",
            highlight_color_2: str = "deeppink",
            font: str = "Arial",  # "Courier New"
    ):
        self.scale = scale
        self.boarder = tuple(b * scale for b in boarder)
        self.lw = lw * scale
        self.chk_light = chk_light
        self.chk_dark = chk_dark
        self.pnt_light = pnt_light
        self.pnt_dark = pnt_dark
        self.bg_light = bg_light
        self.bg_dark = bg_dark
        self.metal_color = metal_color
        self.die_color = die_color
        self.highlight_color_1 = highlight_color_1
        self.highlight_color_2 = highlight_color_2
        self.font = font

    @property
    def point_width(self) -> float:
        return 1.1 * self.scale

    @property
    def point_height(self) -> float:
        return 5.2 * self.scale

    @property
    def point_space(self) -> float:
        return 1.2 * self.scale

    @property
    def bar_width(self) -> float:
        return 1.2 * self.scale

    @property
    def width(self) -> float:
        return 12 * self.point_width + self.bar_width

    @property
    def height(self) -> float:
        return 2 * self.point_height + self.point_space

    @property
    def checkers_height(self) -> float:
        return 0.3 * self.scale

    @property
    def die_size(self) -> float:
        return 0.85 * self.scale

    @property
    def hinge_size(self) -> tuple[float, float]:
        width = 2 / 3 * self.scale
        height = 1.2 * self.scale
        return width, height

    def slot_pos(self, side: str, up: bool) -> tuple[float, float]:
        if side == 'right':
            x = self.width + self.boarder[0] / 2 - self.scale / 2
        elif side == 'left':
            x = -self.boarder[0] / 2 - self.scale / 2
        else:
            raise ValueError(f"unknown side {side}")

        slot_height = 15 * self.checkers_height
        if up:
            y = 0.0
        else:
            y = self.height - slot_height
        return x, y

    def turn_marker_attrs(self, color: Color) -> dict[str, Any]:
        r = 0.15 * self.scale
        x = self.width + self.boarder[0] - r - (self.boarder[1] - 2 * r) / 2
        if color == Color.WHITE:
            fill = self.chk_light
            y = self.height + self.boarder[1] / 2
        elif color == Color.BLACK:
            fill = self.chk_dark
            y = -self.boarder[1] / 2
        else:
            fill = 'gray'
            y = self.height / 2
        return dict(center=(x, y), r=r, fill=fill)

    def doubling_die_pos(self, color: Color) -> tuple[float, float]:
        x, y = self.width / 2, self.height / 2
        if color is Color.WHITE:
            y = self.height - self.scale / 2
        elif color is Color.BLACK:
            y = self.scale / 2
        return x, y

    def pip_text_attrs(self, color: Color, fill: str | None = None, font_size: float | None = None) -> dict[str, Any]:
        if fill is None:
            fill = self.chk_light if color == Color.WHITE else self.chk_dark
        if font_size is None:
            font_size = 0.5 * self.scale

        x, _ = self.slot_pos('right', up=True)
        x += 0.5 * self.scale
        if color == Color.BLACK:
            y = 15 * self.checkers_height + 0.2 * self.scale
        else:
            y = self.height - (15 * self.checkers_height + 0.2 * self.scale)

        return dict(
            insert=(x, y),
            dominant_baseline="auto" if color == Color.WHITE else "hanging",
            text_anchor="middle", font_size=font_size, font_family=self.font, font_weight="bold", fill=fill,
        )

    def point_to_x_updown(self, point: int) -> tuple[float, bool]:
        if point > 12:
            up = False
            i = point - 13
        else:
            up = True
            i = 12 - point
        b = 0 if i < 6 else self.bar_width
        x = b + (i + 0.5) * self.point_width
        return x, up

    def checker_pos(self, pnt: int, n: int = 1) -> tuple[float, float]:
        if pnt < 0:
            pnt = 25 - pnt

        if pnt in (0, 25):
            x = self.width / 2
            i = staple_pos(n, max_n=4)
            if pnt == 0:
                y = self.height / 2 + self.point_space / 2 + i * self.scale
            else:  # pnt == 25
                y = self.height / 2 - self.point_space / 2 - i * self.scale
        elif 1 <= pnt <= 24:
            x, up = self.point_to_x_updown(pnt)
            i = staple_pos(n, max_n=5)
            if up:
                y = self.height - i * self.scale
            else:
                y = i * self.scale
        else:
            raise ValueError(f"{pnt} is not a valid point")

        return x, y
