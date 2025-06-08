"""
Інтерфейси репозиторіїв для роботи з даними
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .models import GameRecord, SavedGame, UserSetting
from ..models import Difficulty


class IGameRecordRepository(ABC):
    """Інтерфейс репозиторію для рекордів ігор"""

    @abstractmethod
    def save(self, record: GameRecord) -> int:
        """Зберігає запис про гру і повертає ID"""
        pass

    @abstractmethod
    def get_by_id(self, record_id: int) -> Optional[GameRecord]:
        """Отримує запис за ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[GameRecord]:
        """Отримує всі записи"""
        pass

    @abstractmethod
    def get_by_difficulty(self, difficulty: Difficulty) -> List[GameRecord]:
        """Отримує записи за рівнем складності"""
        pass

    @abstractmethod
    def get_top_scores(self, limit: int = 10) -> List[GameRecord]:
        """Отримує топ результатів"""
        pass

    @abstractmethod
    def delete(self, record_id: int) -> bool:
        """Видаляє запис"""
        pass


class ISavedGameRepository(ABC):
    """Інтерфейс репозиторію для збережених ігор"""

    @abstractmethod
    def save(self, game: SavedGame) -> int:
        """Зберігає гру і повертає ID"""
        pass

    @abstractmethod
    def get_by_id(self, game_id: int) -> Optional[SavedGame]:
        """Отримує збережену гру за ID"""
        pass

    @abstractmethod
    def get_all(self) -> List[SavedGame]:
        """Отримує всі збережені ігри"""
        pass

    @abstractmethod
    def get_latest(self) -> Optional[SavedGame]:
        """Отримує останню збережену гру"""
        pass

    @abstractmethod
    def update(self, game: SavedGame) -> bool:
        """Оновлює збережену гру"""
        pass

    @abstractmethod
    def delete(self, game_id: int) -> bool:
        """Видаляє збережену гру"""
        pass


class IUserSettingsRepository(ABC):
    """Інтерфейс репозиторію для налаштувань користувача"""

    @abstractmethod
    def save(self, setting: UserSetting) -> int:
        """Зберігає налаштування"""
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[UserSetting]:
        """Отримує налаштування за назвою"""
        pass

    @abstractmethod
    def get_all(self) -> List[UserSetting]:
        """Отримує всі налаштування"""
        pass

    @abstractmethod
    def update(self, setting: UserSetting) -> bool:
        """Оновлює налаштування"""
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        """Видаляє налаштування"""
        pass