from typing import NamedTuple


class Move(NamedTuple):
    src: int
    dst: int
    hit: bool = False

    def to_str(self, bar_off: bool = True, regular: bool = False) -> str:
        src: int | str = self.src
        dst: int | str = self.dst

        if regular and self.src < self.dst:
            src = 25 - src  # type: ignore
            dst = 25 - dst  # type: ignore

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

    @property
    def pips(self) -> int:
        return abs(self.dst - self.src)

    @property
    def bearing_off(self) -> bool:
        return self.dst in (0, 25)
