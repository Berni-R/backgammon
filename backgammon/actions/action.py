from copy import copy as _copy
from typing import Any, Sequence, Iterator, Union
from enum import Enum, auto

from ..core import Color
from ..moves import Move


class Doubling(Enum):
    NO = auto()
    DOUBLE = auto()
    TAKE = auto()
    DROP = auto()


class Action:

    def __init__(self, moves: Sequence[Move] = (), doubling: Doubling = Doubling.NO, copy: bool = False):
        if len(moves) > 1 and doubling != Doubling.NO:
            raise ValueError("Cannot have moves and a doubling action!")
        self.moves = [_copy(m) for m in moves] if copy else list(moves)
        self.doubling = doubling

    def __len__(self) -> int:
        return len(self.moves)

    def __copy__(self) -> 'Action':
        return Action(self.moves, self.doubling, copy=True)

    def copy(self) -> 'Action':
        return self.__copy__()

    def _contract_moves(self) -> list[Move]:
        if len(self.moves) == 0:
            return []
        color = Color.WHITE if self.moves[0].src - self.moves[0].dst > 0 else Color.BLACK

        def contract(moves: list[Move]) -> list[Move]:
            moves = sorted(moves, reverse=color == Color.BLACK)
            contr: list[Move] = []
            while len(moves):
                m1 = moves.pop()
                if m1.hit:
                    contr.append(m1)
                else:
                    for m2 in moves:
                        if m1.dst == m2.src:
                            contr.append(Move(m1.src, m2.dst, m2.hit))
                            moves.remove(m2)
                            break
                    else:
                        contr.append(m1)
            return contr

        contracted = contract(self.moves)
        if len(self.moves) > 2:
            contracted = contract(contracted)

        return contracted

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Action) and (
            self._contract_moves() == other._contract_moves()
            and self.doubling == other.doubling
        )

    def __hash__(self) -> int:
        return hash(tuple(self._contract_moves()) + (self.doubling,))

    @property
    def dances(self) -> bool:
        return len(self.moves) == 0

    def __repr__(self) -> str:
        if self.doubling == Doubling.NO:
            return f"Action({self.moves})"
        else:
            return f"Action({self.moves}, {self.doubling})"

    def to_str(self, bar_off: bool = True, regular: bool = True, stake: int | None = None) -> str:
        if self.doubling == Doubling.DOUBLE:
            if stake is None:
                return 'Doubles'
            else:
                return f'Doubles => {2 * stake}'
        if self.doubling == Doubling.TAKE:
            return 'Takes'
        if self.doubling == Doubling.DROP:
            return 'Drops'
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
            return Action(self.moves[item])
        else:
            raise TypeError(f"cannot subscript Action with type {type(item)}")

    def __add__(self, other: 'Action') -> 'Action':
        if self.doubling != Doubling.NO:
            raise ValueError("cannot add to doubling actions")
        return Action(self.moves + other.moves)

    def __radd__(self, moves: list[Move]) -> 'Action':
        if self.doubling != Doubling.NO:
            raise ValueError("cannot (right) add to doubling actions")
        return Action(moves + self.moves)
