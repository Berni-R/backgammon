from . import core
from . import game
from . import display
from . import agents

# TODO: 1) write function to animate a GameState instance somehow (with adjustable playback speed)
# TODO: 2) write tests for (only) most important functions
# TODO: 4) improve performance, esp. for action generation of double rolls
# TODO: 5) built player for a pytorch model - includes encoding of board
# TODO: 6) actually train this player in self-play with reinforcement learning

from .core import (
    Color, WinType, GameResult, IllegalMoveError, ImpossibleMoveError,
    Move, Board,
)
from .game import (
    assert_legal_move, is_legal_move, build_legal_move, build_legal_moves,
    GameState,
    ActionType, Action, Transition,
    Agent, Game, Match,
)
from .agents import RandomAgent, SimpleAgent
