from typing import Collection, Iterable
from dataclasses import dataclass
from enum import Enum, auto
import random

from ..core import Color, GameResult, WinType, Move, GameState
from .agent import Agent


class ActionType(Enum):
    NONE = 0
    MOVE = auto()
    DOUBLE = auto()
    TAKE = auto()
    DROP = auto()
    DICEROLL = auto()
    FINISH_TURN = auto()


@dataclass(slots=True)
class Action:
    move: Move | None
    type: ActionType = ActionType.MOVE


@dataclass(slots=True)
class Transition:
    state: GameState
    action: Action
    next_state: GameState
    reward: int


class Game:

    def __init__(self, state: GameState | None = None):
        self.state = GameState() if state is None else state.copy()
        self.moves: list[tuple[int, Move]] = []
        self.history: list[Transition] = []

    def _first_move(self) -> bool:
        if len(self.history) == 0:
            return True
        if len(self.history) > 4:  # doubling, take, move, [move]
            return False
        n_moves = sum(1 for t in self.history if t.action.type == ActionType.MOVE)
        n_used = sum(1 for used in self.state.dice_used if used)
        return n_moves == n_used

    def _repr_svg_(self) -> str:
        from ..display import DisplayStyle, get_dice_colors, svg_gamestate
        ds = DisplayStyle()
        last_move = self.moves[-1][1] if len(self.moves) else None
        dice_colors = get_dice_colors(dice=self.state.dice, game_start=self._first_move(), state=self.state, ds=ds)
        return svg_gamestate(self.state, last_move=last_move, dice_colors=dice_colors).tostring()

    def sample_history(self, batch_size: int, filter_types: Collection[ActionType] | None = None) -> list[Transition]:
        if filter_types is None:
            history = self.history
        else:
            history = [t for t in self.history if t.action.type in filter_types]
        if len(history) == 0:
            return []
        return random.sample(history, batch_size)

    @property
    def turn(self) -> Color:
        return self.state.turn

    def resigned(self) -> bool:
        return len(self.history) > 0 and self.history[-1].action.type == ActionType.DROP

    def game_over(self) -> bool:
        return self.resigned() or self.state.board.game_over()

    def do_move(self, move: Move) -> 'Game':
        state = self.state.copy()
        i = self.state.do_move(move)
        reward = self.state.result().stake if self.state.board.game_over() else 0
        self.history.append(Transition(state, Action(move), self.state.copy(), reward))
        self.moves.append((i, move))
        return self

    def undo_move(self, checked: bool = True) -> bool:
        if len(self.moves) == 0:
            return False
        i, move = self.moves.pop()
        self.state.undo_move(move, i, checked=checked)
        self.history.pop()
        return True

    def finish_turn(self):
        self.moves = []
        self.state.finish_turn()

    def result(self) -> GameResult:
        if self.resigned():
            # doubling_turn could still be NONE, turn is sure
            return GameResult(self.state.turn, self.state.stake, WinType.NORMAL)
        return self.state.result()

    def _step(
            self,
            agents: Agent | dict[Color, Agent],
            points: Iterable[int] = (0, 0),
            match_ends_at: int = 1,
            allow_doubling: bool = True,
    ) -> tuple[Action | None, int]:
        if self.game_over():
            return None, self.result().stake

        if isinstance(agents, Agent):
            agents = {Color.BLACK: agents, Color.WHITE: agents}

        if len(self.history) > 0 and self.history[-1].action.type == ActionType.DOUBLE:
            agent = agents[self.state.turn.other()]
            if agent.will_take_doubling(self.state, points, match_ends_at):
                action = Action(None, ActionType.TAKE)
                self.state.doubling_turn = self.state.turn.other()
                self.state.stake *= 2
                return action, 0
            else:
                action = Action(None, ActionType.DROP)
                return action, -self.state.stake  # WinType is always NORMAL

        if len(self.state.dice) == 0:
            if allow_doubling and len(self.history) > 0 and self.state.can_couble():
                agent = agents[self.state.turn]
                if agent.will_double(self.state, points, match_ends_at):
                    action = Action(None, ActionType.DOUBLE)
                    return action, 0

            self.state.roll_dice()
            return Action(None, ActionType.DICEROLL), 0

        if len(self.state.build_legal_moves()) == 0:
            self.finish_turn()
            return Action(None, ActionType.FINISH_TURN), 0

        agent = agents[self.state.turn]
        move = agent.choose_move(self.state)
        self.do_move(move)
        return Action(move), self.history[-1].reward

    def step(
            self,
            agents: Agent | dict[Color, Agent],
            points: Iterable[int] = (0, 0),
            match_ends_at: int = 1,
            allow_doubling: bool = True,
    ) -> Action | None:
        prev_state = self.state.copy()
        action, reward = self._step(agents, points, match_ends_at, allow_doubling)
        if action is not None and action.type != ActionType.MOVE:
            transition = Transition(prev_state, action, self.state.copy(), reward)
            self.history.append(transition)
        return action
