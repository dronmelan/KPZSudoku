# sudoku/database/__init__.py
"""
Пакет для роботи з базою даних
"""
from .models import GameRecord, SavedGame, UserSetting
from .repositories import IGameRecordRepository, ISavedGameRepository, IUserSettingsRepository
from .sqlite_repositories import SQLiteGameRecordRepository, SQLiteSavedGameRepository, SQLiteUserSettingsRepository
from .database_manager import DatabaseManager
from .services import GameRecordService, SavedGameService, UserSettingsService
from .database_factory import DatabaseFactory

__all__ = [
    # Models
    'GameRecord', 'SavedGame', 'UserSetting',
    # Repository interfaces
    'IGameRecordRepository', 'ISavedGameRepository', 'IUserSettingsRepository',
    # Repository implementations
    'SQLiteGameRecordRepository', 'SQLiteSavedGameRepository', 'SQLiteUserSettingsRepository',
    # Database manager
    'DatabaseManager',
    # Services
    'GameRecordService', 'SavedGameService', 'UserSettingsService',
    # Factory
    'DatabaseFactory'
]