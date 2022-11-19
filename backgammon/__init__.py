from . import core
from . import moves
from . import board
from . import display
from . import actions
from . import players
from . import game
from . import match

# TODO: 1) write function to animate a Game instance somehow (with adjustable playback speed)
# TODO: 2) write tests for (only) most important functions
# TODO: 4) improve performance, esp. for action generation of double rolls
# TODO: 5) built player for a pytorch model - includes encoding of board
# TODO: 6) actually train this player in self-play with reinforcement learning

from .core import Color, roll_dice, GameResult, IllegalMoveError, ImpossibleMoveError
from .moves import (
    Move,
    assert_legal_move, is_legal_move, build_legal_move, build_legal_moves
)
from .board import Board
from .display import board_ascii_art, print_board
from .actions import (
    Action,
    assert_legal_action, is_legal_action,
    do_action, undo_action, build_legal_actions
)
from .players import Player
from .players import RandomPlayer, SimplePlayer
from .game import Game
from .match import Match
