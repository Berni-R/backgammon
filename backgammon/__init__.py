from . import core
from . import move
from . import board
from . import legal_actions
from . import players
from . import game
from . import rating
from . import match

# TODO: 1) write function to animate a Game instance somehow (with adjustable playback speed)
# TODO: 2) write tests for (only) most important functions
# TODO: 3) improve performance, esp. for action generation of double rolls
# TODO: 4) Built player for a pytorch model - includes encoding of board
# TODO: 5) Actually train this player in self-play with reinforcement learning

from .core import Color, GameResult, IllegalMoveError, ImpossibleMoveError
from .move import Move
from .board import Board
from .legal_actions import (
    Action,
    build_legal_move, build_legal_moves,
    is_legal_move, is_legal_action,
    do_action, undo_action, build_legal_actions
)
from .players import Player
from .players import RandomPlayer, SimplePlayer
from .game import roll_dice, Game
from .rating import FIBSRating
from .match import Match
