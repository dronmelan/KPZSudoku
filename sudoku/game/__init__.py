"""
Пакет для основних компонентів гри
"""
from .game import Game
from .states.game_over_state import GameOverState
from .states.i_game_state import IGameState
from .states.paused_state import PausedState
from .states.playing_state import PlayingState

from .timer import GameTimer

__all__ = ['Game', 'IGameState', 'PlayingState', 'GameOverState', 'PausedState', 'GameTimer']