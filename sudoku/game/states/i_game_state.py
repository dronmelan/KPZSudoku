import pygame

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from ..game import Game

class IGameState(ABC):
    """Інтерфейс для стану гри"""
    @abstractmethod
    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        """Обробляє подію гри"""
        pass

    @abstractmethod
    def update(self, game: 'Game') -> None:
        """Оновлює стан гри"""
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображає стан гри"""
        pass
