import numpy as np
from typing import NamedTuple


class Move(NamedTuple):
    src: int
    dst: int
    hit: bool = False

    def to_str(self, bar_off: bool = True, regular: bool = True) -> str:
        if regular and self.src < self.dst:
            return self.flipped().to_str(bar_off, regular=False)
        src: int | str = self.src
        dst: int | str = self.dst
        if bar_off:
            # it is impossible to move from off or to bar
            src = 'bar' if self.src in (0, 25) else src
            dst = 'off' if self.dst in (0, 25) else dst
        s = f'{src}/{dst}'
        if self.hit:
            s += '*'
        return s

    def __str__(self) -> str:
        return self.to_str()

    def __repr__(self) -> str:
        return f'Move({self.src}, {self.dst}' + ('' if self.hit is False else f', hit={self.hit}') + ')'

    def flipped(self) -> 'Move':
        return Move(25 - self.src, 25 - self.dst, self.hit)

    @property
    def pips(self) -> int:
        return abs(self.dst - self.src)

    @property
    def bearing_off(self) -> bool:
        return self.dst in (0, 25)

    def assert_consistent_data(self):
        if not isinstance(self.src, int | np.int_):
            raise TypeError(f"`src` needs to be an integer, but is {self.src} ({type(self.src)}).")
        if not isinstance(self.dst, int | np.int_):
            raise TypeError(f"`dst` needs to be an integer, but is {self.dst} ({type(self.dst)}.")
        if not isinstance(self.hit, bool | np.bool_):
            raise TypeError(f"`hit` needs to be a boolean value, but is {self.hit} ({type(self.hit)}).")

        if not 0 <= self.src <= 25:
            raise ValueError(f"`src` needs to be in [0, 25], but is {self.src}.")
        if not 0 <= self.dst <= 25:
            raise ValueError(f"`dst` needs to be in [0, 25], but is {self.dst}.")
        if self.hit and self.dst in (0, 25):
            raise ValueError("impossible to hit when bearing off")
