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
            font: str = "Open Sans",  # "Arial",
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

    def point_to_x_updown(self, point: int) -> tuple[float, bool]:
        if point > 12:
            up = True
            i = point - 13
        else:
            up = False
            i = 12 - point
        b = 0 if i < 6 else self.bar_width
        x = b + (i + 0.5) * self.point_width
        return x, up
