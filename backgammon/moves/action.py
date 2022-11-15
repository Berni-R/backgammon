from typing import Any, Sequence, Optional, Iterator, Union

from .move import Move


class Action:

    def __init__(self, moves: Sequence[Move] = (), doubles: int = 0, takes: Optional[bool] = None):
        self.moves = [] if doubles else [m for m in moves]
        self.doubles = doubles
        self.takes = takes

    def __copy__(self) -> 'Action':
        return Action(
            [move for move in self.moves],
            self.doubles,
            self.takes,
        )

    def copy(self) -> 'Action':
        return self.__copy__()

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Action) and (
            # set(self.moves) == set(other.moves)
            len(self.moves) == len(other.moves)
            and all(a == b for a, b in zip(self.moves, other.moves))
            and self.doubles == other.doubles
            and self.takes == other.takes
        )

    def __hash__(self) -> int:
        return hash(tuple(self.moves) + (self.doubles, self.takes))

    @property
    def is_dropping(self) -> bool:
        return self.takes is not None and not self.takes

    @property
    def dances(self) -> bool:
        return len(self.moves) == 0 and (not self.doubles)

    def __repr__(self) -> str:
        r = f"Action({self.moves}"
        if self.doubles:
            r += f", doubles={self.doubles}"
        if self.takes is not None:
            r += f", takes={self.takes}"
        return r + ")"

    def to_str(self, bar_off: bool = True, regular: bool = True) -> str:
        if self.takes is not None:
            return 'Takes' if self.takes else 'Drops'
        if self.doubles:
            return f'Doubles => {self.doubles}'
        if len(self.moves) == 0:
            return 'Dances'
        return ' '.join(move.to_str(bar_off, regular) for move in self.moves)

    def __str__(self) -> str:
        return self.to_str()

    def __iter__(self) -> Iterator[Move]:
        return iter(self.moves)

    def __getitem__(self, item: int | slice) -> Union[Move, 'Action']:
        if isinstance(item, int):
            return self.moves[item]
        elif isinstance(item, slice):
            return Action(self.moves[item], self.doubles, self.takes)
        else:
            raise TypeError(f"cannot subscript Action with type {type(item)}")

    def __add__(self, other: 'Action') -> 'Action':
        if self.doubles != 0 or other.doubles:
            raise ValueError("cannot add to doubling actions")
        return Action(self.moves + other.moves)

    def __radd__(self, moves: list[Move]) -> 'Action':
        if self.doubles != 0:
            raise ValueError("cannot (right) add to doubling action")
        return Action(moves + self.moves)
