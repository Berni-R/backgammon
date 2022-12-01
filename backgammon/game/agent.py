from abc import ABC, abstractmethod
from typing import Iterable

from ..core import Move
from .game_state import GameState


class Agent(ABC):

    def __repr__(self) -> str:
        import inspect

        try:
            attrs = []
            signature = inspect.signature(self.__init__)  # type: ignore
            for arg, p in signature.parameters.items():
                val = getattr(self, arg) if hasattr(self, arg) else getattr(self, '_' + arg)
                if val != p.default:
                    attrs.append(f'{arg}={val}')
        except AttributeError:
            attrs = ["..."]

        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @abstractmethod
    def choose_move(self, state: GameState) -> Move:
        ...

    @abstractmethod
    def will_double(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        ...

    @abstractmethod
    def will_take_doubling(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        ...
