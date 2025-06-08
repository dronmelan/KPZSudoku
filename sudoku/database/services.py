"""
Сервісний шар для бізнес-логіки роботи з базою даних
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from .repositories import IGameRecordRepository, ISavedGameRepository, IUserSettingsRepository
from .models import GameRecord, SavedGame, UserSetting
from ..models import Difficulty, Cell
from ..utils.helpers import calculate_difficulty_score


class GameRecordService:
    """Сервіс для роботи з рекордами ігор"""

    def __init__(self, repository: IGameRecordRepository):
        self.repository = repository

    def save_game_record(self, difficulty: Difficulty, completion_time: int, hints_used: int) -> int:
        """Зберігає новий рекорд гри"""
        score = calculate_difficulty_score(difficulty.name, completion_time, hints_used)

        record = GameRecord(
            id=None,
            difficulty=difficulty,
            completion_time=completion_time,
            hints_used=hints_used,
            score=score,
            date_completed=datetime.now()
        )

        return self.repository.save(record)

    def get_leaderboard(self, difficulty: Optional[Difficulty] = None, limit: int = 10) -> List[GameRecord]:
        """Отримує таблицю лідерів"""
        if difficulty:
            records = self.repository.get_by_difficulty(difficulty)
            return records[:limit]
        else:
            return self.repository.get_top_scores(limit)

    def get_personal_stats(self) -> Dict[str, Any]:
        """Отримує персональну статистику гравця"""
        all_records = self.repository.get_all()

        if not all_records:
            return {
                'total_games': 0,
                'total_time': 0,
                'average_time': 0,
                'best_scores': {},
                'games_by_difficulty': {}
            }

        stats = {
            'total_games': len(all_records),
            'total_time': sum(r.completion_time for r in all_records),
            'average_time': sum(r.completion_time for r in all_records) // len(all_records),
            'best_scores': {},
            'games_by_difficulty': {}
        }

        # Статистика по складності
        for difficulty in Difficulty:
            difficulty_records = [r for r in all_records if r.difficulty == difficulty]
            if difficulty_records:
                best_record = max(difficulty_records, key=lambda x: x.score)
                stats['best_scores'][difficulty.name] = {
                    'score': best_record.score,
                    'time': best_record.completion_time,
                    'hints_used': best_record.hints_used
                }
                stats['games_by_difficulty'][difficulty.name] = len(difficulty_records)

        return stats

    def delete_record(self, record_id: int) -> bool:
        """Видаляє запис"""
        return self.repository.delete(record_id)


class SavedGameService:
    """Сервіс для роботи зі збереженими іграми"""

    def __init__(self, repository: ISavedGameRepository):
        self.repository = repository

    def save_game(self, difficulty: Difficulty, grid: List[List[Cell]],
                  solution: List[List[int]], elapsed_time: int, hints_used: int) -> int:
        """Зберігає поточну гру"""
        # Конвертуємо сітку клітинок у JSON-серіалізовану форму
        grid_data = [[cell.to_dict() for cell in row] for row in grid]

        saved_game = SavedGame(
            id=None,
            difficulty=difficulty,
            current_state=grid_data,
            solution=solution,
            elapsed_time=elapsed_time,
            hints_used=hints_used,
            date_saved=datetime.now()
        )

        return self.repository.save(saved_game)

    def load_game(self, game_id: int) -> Optional[SavedGame]:
        """Завантажує збережену гру"""
        return self.repository.get_by_id(game_id)

    def get_all_saves(self) -> List[SavedGame]:
        """Отримує всі збережені ігри"""
        return self.repository.get_all()

    def get_latest_save(self) -> Optional[SavedGame]:
        """Отримує останнє збереження"""
        return self.repository.get_latest()

    def update_save(self, saved_game: SavedGame) -> bool:
        """Оновлює збережену гру"""
        saved_game.date_saved = datetime.now()
        return self.repository.update(saved_game)

    def delete_save(self, game_id: int) -> bool:
        """Видаляє збережену гру"""
        return self.repository.delete(game_id)

    def has_saves(self) -> bool:
        """Перевіряє, чи є збережені ігри"""
        saves = self.repository.get_all()
        return len(saves) > 0


class UserSettingsService:
    """Сервіс для роботи з налаштуваннями користувача"""

    def __init__(self, repository: IUserSettingsRepository):
        self.repository = repository

    def get_setting(self, name: str, default_value: str = None) -> Optional[str]:
        """Отримує значення налаштування за назвою"""
        setting = self.repository.get_by_name(name)
        if setting:
            return setting.setting_value
        return default_value

    def set_setting(self, name: str, value: str) -> bool:
        """Встановлює значення налаштування"""
        existing_setting = self.repository.get_by_name(name)

        if existing_setting:
            # Оновлюємо існуюче налаштування
            existing_setting.setting_value = value
            return self.repository.update(existing_setting)
        else:
            # Створюємо нове налаштування
            new_setting = UserSetting(
                id=None,
                setting_name=name,
                setting_value=value
            )
            self.repository.save(new_setting)
            return True

    def get_all_settings(self) -> Dict[str, str]:
        """Отримує всі налаштування у вигляді словника"""
        settings = self.repository.get_all()
        return {setting.setting_name: setting.setting_value for setting in settings}

    def get_theme(self) -> str:
        """Отримує поточну тему"""
        return self.get_setting('theme', 'light')

    def set_theme(self, theme: str) -> bool:
        """Встановлює тему (light/dark)"""
        if theme not in ['light', 'dark']:
            raise ValueError("Theme must be 'light' or 'dark'")
        return self.set_setting('theme', theme)

    def is_sound_enabled(self) -> bool:
        """Перевіряє, чи увімкнений звук"""
        return self.get_setting('sound_enabled', 'true').lower() == 'true'

    def set_sound_enabled(self, enabled: bool) -> bool:
        """Встановлює статус звуку"""
        return self.set_setting('sound_enabled', str(enabled).lower())

    def is_auto_notes_enabled(self) -> bool:
        """Перевіряє, чи увімкнені автоматичні нотатки"""
        return self.get_setting('auto_notes', 'false').lower() == 'true'

    def set_auto_notes_enabled(self, enabled: bool) -> bool:
        """Встановлює статус автоматичних нотаток"""
        return self.set_setting('auto_notes', str(enabled).lower())

    def is_highlight_conflicts_enabled(self) -> bool:
        """Перевіряє, чи увімкнене підсвічування конфліктів"""
        return self.get_setting('highlight_conflicts', 'true').lower() == 'true'

    def set_highlight_conflicts_enabled(self, enabled: bool) -> bool:
        """Встановлює статус підсвічування конфліктів"""
        return self.set_setting('highlight_conflicts', str(enabled).lower())

    def is_timer_shown(self) -> bool:
        """Перевіряє, чи показується таймер"""
        return self.get_setting('show_timer', 'true').lower() == 'true'

    def set_timer_shown(self, shown: bool) -> bool:
        """Встановлює, чи показувати таймер"""
        return self.set_setting('show_timer', str(shown).lower())

    def get_max_hints(self) -> int:
        """Отримує максимальну кількість підказок"""
        try:
            return int(self.get_setting('max_hints', '5'))
        except (ValueError, TypeError):
            return 5

    def set_max_hints(self, max_hints: int) -> bool:
        """Встановлює максимальну кількість підказок"""
        if max_hints < 0:
            raise ValueError("Max hints cannot be negative")
        return self.set_setting('max_hints', str(max_hints))

    def get_difficulty_preference(self) -> Optional[str]:
        """Отримує переважний рівень складності"""
        return self.get_setting('preferred_difficulty')

    def set_difficulty_preference(self, difficulty: str) -> bool:
        """Встановлює переважний рівень складності"""
        valid_difficulties = ['EASY', 'MEDIUM', 'HARD']
        if difficulty.upper() not in valid_difficulties:
            raise ValueError(f"Difficulty must be one of: {valid_difficulties}")
        return self.set_setting('preferred_difficulty', difficulty.upper())

    def reset_settings(self) -> bool:
        """Скидає всі налаштування до значень за замовчуванням"""
        default_settings = {
            'theme': 'light',
            'sound_enabled': 'true',
            'auto_notes': 'false',
            'highlight_conflicts': 'true',
            'show_timer': 'true',
            'max_hints': '5'
        }

        success = True
        for name, value in default_settings.items():
            if not self.set_setting(name, value):
                success = False

        return success

    def delete_setting(self, name: str) -> bool:
        """Видаляє налаштування"""
        return self.repository.delete(name)

    def export_settings(self) -> Dict[str, str]:
        """Експортує налаштування для бекапу"""
        return self.get_all_settings()

    def import_settings(self, settings: Dict[str, str]) -> bool:
        """Імпортує налаштування з бекапу"""
        success = True
        for name, value in settings.items():
            if not self.set_setting(name, value):
                success = False
        return success