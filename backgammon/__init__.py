from . import core
from . import moves
from . import board
from . import game_state
from . import game
from . import display
from . import agents
from . import match

# TODO: 1) write function to animate a GameState instance somehow (with adjustable playback speed)
# TODO: 2) write tests for (only) most important functions
# TODO: 4) improve performance, esp. for action generation of double rolls
# TODO: 5) built player for a pytorch model - includes encoding of board
# TODO: 6) actually train this player in self-play with reinforcement learning

from .core import Color, roll_dice, WinType, GameResult, IllegalMoveError, ImpossibleMoveError
from .moves import (
    Move,
    assert_legal_move, is_legal_move, build_legal_move, build_legal_moves
)
from .board import Board
from .game_state import GameState
from .game import (
    ActionType, Action, Transition,
    Game,
)
from .display import (
    board_ascii_art, print_board,
    DisplayStyle, BoardDrawing,
    svg_board, svg_gamestate,
)
from .agents import Agent, RandomAgent, SimpleAgent
from .match import Match
