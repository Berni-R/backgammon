from typing import Iterable

from backgammon import GameState, Move
from backgammon.game.agent import Agent


class SomeAgent(Agent):

    def __init__(self, name: str, answer: float = 42):
        self.name = name
        self.answer = answer

    def choose_move(self, state: GameState) -> Move:
        return NotImplemented

    def will_double(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        return NotImplemented

    def will_take_doubling(self, state: GameState, points: Iterable[int], match_ends_at: int) -> bool:
        return NotImplemented


def test_agent_repr():
    agent = SomeAgent("Smith", answer=1)
    assert repr(agent) == "SomeAgent(name='Smith', answer=1)"

    agent = SomeAgent("Paul")
    assert repr(agent) == "SomeAgent(name='Paul')"

    agent = SomeAgent("Killer")
    del agent.name
    assert repr(agent) == "SomeAgent(...)"
