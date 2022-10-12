from . import core
from . import moves
from . import board
from . import players
from . import game
from . import rating
from . import match

# TODO: 1) write function to animate a Game instance somehow (with adjustable playback speed)
# TODO: 2) write tests for (only) most important functions
# TODO: 3) build framework for tournaments, that can assign ratings / rankings to multiple players at once efficiently
# TODO: 4) improve performance, esp. for action generation of double rolls
# TODO: 5) built player for a pytorch model - includes encoding of board
# TODO: 6) actually train this player in self-play with reinforcement learning

from .core import Color, GameResult, IllegalMoveError, ImpossibleMoveError
from .moves import (
    Move,
    assert_legal_move, is_legal_move, build_legal_move, build_legal_moves, legal_actions,
    Action,
    assert_legal_action, is_legal_action,
    do_action, undo_action, build_legal_actions
)
from .board import Board
from .players import Player
from .players import RandomPlayer, SimplePlayer
from .game import roll_dice, Game
from .rating import FIBSRating
from .match import Match
