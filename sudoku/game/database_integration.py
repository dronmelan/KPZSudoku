"""
Модуль для інтеграції бази даних з грою
"""
from typing import Optional, List, Dict, Any
import logging

from ..database import (
    DatabaseManager,
    GameRecordService,
    SavedGameService,
    UserSettingsService,
    SQLiteGameRecordRepository,
    SQLiteSavedGameRepository,
    SQLiteUserSettingsRepository
)
from ..models import Difficulty, Cell


class GameDatabaseManager:
    """Менеджер для роботи з базою даних в грі"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_manager = DatabaseManager(db_path)

        # Ініціалізуємо базу даних
        try:
            self.db_manager.initialize_database()

            # Створюємо репозиторії
            self.game_record_repo = SQLiteGameRecordRepository(self.db_manager)
            self.saved_game_repo = SQLiteSavedGameRepository(self.db_manager)
            self.user_settings_repo = SQLiteUserSettingsRepository(self.db_manager)

            # Створюємо сервіси
            self.game_record_service = GameRecordService(self.game_record_repo)
            self.saved_game_service = SavedGameService(self.saved_game_repo)
            self.user_settings_service = UserSettingsService(self.user_settings_repo)

            logging.info("Database successfully initialized")

        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            raise

    def save_game_record(self, difficulty: Difficulty, completion_time: int, hints_used: int) -> bool:
        """Зберігає результат завершеної гри"""
        try:
            record_id = self.game_record_service.save_game_record(
                difficulty, completion_time, hints_used
            )
            logging.info(f"Game record saved with ID: {record_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to save game record: {e}")
            return False

    def save_current_game(self, difficulty: Difficulty, grid: List[List[Cell]],
                          solution: List[List[int]], elapsed_time: int, hints_used: int) -> bool:
        """Зберігає поточну гру"""
        try:
            game_id = self.saved_game_service.save_game(
                difficulty, grid, solution, elapsed_time, hints_used
            )
            logging.info(f"Game saved with ID: {game_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to save game: {e}")
            return False

    def load_latest_game(self):
        """Завантажує останню збережену гру"""
        try:
            return self.saved_game_service.get_latest_save()
        except Exception as e:
            logging.error(f"Failed to load latest game: {e}")
            return None

    def get_all_saved_games(self):
        """Отримує всі збережені ігри"""
        try:
            return self.saved_game_service.get_all_saves()
        except Exception as e:
            logging.error(f"Failed to get saved games: {e}")
            return []

    def delete_saved_game(self, game_id: int) -> bool:
        """Видаляє збережену гру"""
        try:
            return self.saved_game_service.delete_save(game_id)
        except Exception as e:
            logging.error(f"Failed to delete saved game: {e}")
            return False

    def has_saved_games(self) -> bool:
        """Перевіряє, чи є збережені ігри"""
        try:
            return self.saved_game_service.has_saves()
        except Exception as e:
            logging.error(f"Failed to check for saved games: {e}")
            return False

    def get_leaderboard(self, difficulty: Optional[Difficulty] = None, limit: int = 10):
        """Отримує таблицю лідерів"""
        try:
            return self.game_record_service.get_leaderboard(difficulty, limit)
        except Exception as e:
            logging.error(f"Failed to get leaderboard: {e}")
            return []

    def get_personal_stats(self) -> Dict[str, Any]:
        """Отримує персональну статистику"""
        try:
            return self.game_record_service.get_personal_stats()
        except Exception as e:
            logging.error(f"Failed to get personal stats: {e}")
            return {}

    # Методи для роботи з налаштуваннями
    def get_user_setting(self, name: str, default_value: str = None) -> Optional[str]:
        """Отримує налаштування користувача"""
        try:
            return self.user_settings_service.get_setting(name, default_value)
        except Exception as e:
            logging.error(f"Failed to get user setting {name}: {e}")
            return default_value

    def set_user_setting(self, name: str, value: str) -> bool:
        """Встановлює налаштування користувача"""
        try:
            return self.user_settings_service.set_setting(name, value)
        except Exception as e:
            logging.error(f"Failed to set user setting {name}: {e}")
            return False

    def get_theme(self) -> str:
        """Отримує поточну тему"""
        return self.user_settings_service.get_theme()

    def set_theme(self, theme: str) -> bool:
        """Встановлює тему"""
        try:
            return self.user_settings_service.set_theme(theme)
        except Exception as e:
            logging.error(f"Failed to set theme: {e}")
            return False

    def is_sound_enabled(self) -> bool:
        """Перевіряє, чи увімкнений звук"""
        return self.user_settings_service.is_sound_enabled()

    def set_sound_enabled(self, enabled: bool) -> bool:
        """Встановлює статус звуку"""
        try:
            return self.user_settings_service.set_sound_enabled(enabled)
        except Exception as e:
            logging.error(f"Failed to set sound setting: {e}")
            return False

    def get_max_hints(self) -> int:
        """Отримує максимальну кількість підказок"""
        return self.user_settings_service.get_max_hints()

    def set_max_hints(self, max_hints: int) -> bool:
        """Встановлює максимальну кількість підказок"""
        try:
            return self.user_settings_service.set_max_hints(max_hints)
        except Exception as e:
            logging.error(f"Failed to set max hints: {e}")
            return False

    def close(self):
        """Закриває з'єднання з базою даних"""
        try:
            self.db_manager.disconnect()
        except Exception as e:
            logging.error(f"Failed to close database connection: {e}")

    def __enter__(self):
        """Контекстний менеджер - вхід"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстний менеджер - вихід"""
        self.close()
