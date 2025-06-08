"""
Фабрика для створення та ініціалізації бази даних
"""
from typing import Tuple
from .database_manager import DatabaseManager
from .sqlite_repositories import (
    SQLiteGameRecordRepository,
    SQLiteSavedGameRepository,
    SQLiteUserSettingsRepository
)
from .services import GameRecordService, SavedGameService, UserSettingsService


class DatabaseFactory:
    """Фабрика для створення всіх компонентів бази даних"""

    def __init__(self, db_path: str = None):
        self.db_manager = DatabaseManager(db_path)

    def initialize(self) -> Tuple[GameRecordService, SavedGameService, UserSettingsService]:
        """
        Ініціалізує базу даних та повертає всі сервіси
        """
        self.db_manager.connect()
        self.db_manager.initialize_database()

        game_record_repo = SQLiteGameRecordRepository(self.db_manager)
        saved_game_repo = SQLiteSavedGameRepository(self.db_manager)
        user_settings_repo = SQLiteUserSettingsRepository(self.db_manager)

        game_record_service = GameRecordService(game_record_repo)
        saved_game_service = SavedGameService(saved_game_repo)
        user_settings_service = UserSettingsService(user_settings_repo)

        return game_record_service, saved_game_service, user_settings_service

    def close(self):
        """Закриває з'єднання з базою даних"""
        self.db_manager.disconnect()

