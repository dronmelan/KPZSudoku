"""
SQLite реалізації репозиторіїв
"""
import sqlite3
from typing import List, Optional
from datetime import datetime

from .repositories import IGameRecordRepository, ISavedGameRepository, IUserSettingsRepository
from .models import GameRecord, SavedGame, UserSetting
from .database_manager import DatabaseManager
from ..models import Difficulty


class SQLiteGameRecordRepository(IGameRecordRepository):
    """SQLite реалізація репозиторію для рекордів ігор"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, record: GameRecord) -> int:
        """Зберігає запис про гру і повертає ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            INSERT INTO game_records (difficulty, completion_time, hints_used, score, date_completed)
            VALUES (?, ?, ?, ?, ?)
        """, (
            record.difficulty.name,
            record.completion_time,
            record.hints_used,
            record.score,
            record.date_completed.isoformat()
        ))

        conn.commit()
        return cursor.lastrowid

    def get_by_id(self, record_id: int) -> Optional[GameRecord]:
        """Отримує запис за ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records WHERE id = ?
        """, (record_id,))

        row = cursor.fetchone()
        if row:
            return GameRecord.from_dict(dict(row))
        return None

    def get_all(self) -> List[GameRecord]:
        """Отримує всі записи"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records ORDER BY date_completed DESC
        """)

        return [GameRecord.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_by_difficulty(self, difficulty: Difficulty) -> List[GameRecord]:
        """Отримує записи за рівнем складності"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records 
            WHERE difficulty = ? 
            ORDER BY score DESC, completion_time ASC
        """, (difficulty.name,))

        return [GameRecord.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_top_scores(self, limit: int = 10) -> List[GameRecord]:
        """Отримує топ результатів"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM game_records 
            ORDER BY score DESC, completion_time ASC 
            LIMIT ?
        """, (limit,))

        return [GameRecord.from_dict(dict(row)) for row in cursor.fetchall()]

    def delete(self, record_id: int) -> bool:
        """Видаляє запис"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            DELETE FROM game_records WHERE id = ?
        """, (record_id,))

        conn.commit()
        return cursor.rowcount > 0


class SQLiteSavedGameRepository(ISavedGameRepository):
    """SQLite реалізація репозиторію для збережених ігор"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, game: SavedGame) -> int:
        """Зберігає гру і повертає ID"""
        conn = self.db_manager.get_connection()

        if game.id is None:
            # Створення нового запису
            cursor = conn.execute("""
                INSERT INTO saved_games (difficulty, current_state, solution, elapsed_time, hints_used, date_saved)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                game.difficulty.name,
                game.to_dict()['current_state'],
                game.to_dict()['solution'],
                game.elapsed_time,
                game.hints_used,
                game.date_saved.isoformat()
            ))
            game_id = cursor.lastrowid
        else:
            # Оновлення існуючого запису
            conn.execute("""
                UPDATE saved_games 
                SET current_state = ?, elapsed_time = ?, hints_used = ?, 
                    date_saved = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                game.to_dict()['current_state'],
                game.elapsed_time,
                game.hints_used,
                game.date_saved.isoformat(),
                game.id
            ))
            game_id = game.id

        conn.commit()
        return game_id

    def get_by_id(self, game_id: int) -> Optional[SavedGame]:
        """Отримує збережену гру за ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM saved_games WHERE id = ?
        """, (game_id,))

        row = cursor.fetchone()
        if row:
            return SavedGame.from_dict(dict(row))
        return None

    def get_all(self) -> List[SavedGame]:
        """Отримує всі збережені ігри"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM saved_games ORDER BY date_saved DESC
        """)

        return [SavedGame.from_dict(dict(row)) for row in cursor.fetchall()]

    def get_latest(self) -> Optional[SavedGame]:
        """Отримує останню збережену гру"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM saved_games ORDER BY date_saved DESC LIMIT 1
        """)

        row = cursor.fetchone()
        if row:
            return SavedGame.from_dict(dict(row))
        return None

    def update(self, game: SavedGame) -> bool:
        """Оновлює збережену гру"""
        if game.id is None:
            return False

        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            UPDATE saved_games 
            SET difficulty = ?, current_state = ?, solution = ?, elapsed_time = ?, 
                hints_used = ?, date_saved = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            game.difficulty.name,
            game.to_dict()['current_state'],
            game.to_dict()['solution'],
            game.elapsed_time,
            game.hints_used,
            game.date_saved.isoformat(),
            game.id
        ))

        conn.commit()
        return cursor.rowcount > 0

    def delete(self, game_id: int) -> bool:
        """Видаляє збережену гру"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            DELETE FROM saved_games WHERE id = ?
        """, (game_id,))

        conn.commit()
        return cursor.rowcount > 0


class SQLiteUserSettingsRepository(IUserSettingsRepository):
    """SQLite реалізація репозиторію для налаштувань користувача"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save(self, setting: UserSetting) -> int:
        """Зберігає налаштування"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            INSERT OR REPLACE INTO user_settings (setting_name, setting_value)
            VALUES (?, ?)
        """, (setting.setting_name, setting.setting_value))

        conn.commit()
        return cursor.lastrowid

    def get_by_name(self, name: str) -> Optional[UserSetting]:
        """Отримує налаштування за назвою"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM user_settings WHERE setting_name = ?
        """, (name,))

        row = cursor.fetchone()
        if row:
            return UserSetting.from_dict(dict(row))
        return None

    def get_all(self) -> List[UserSetting]:
        """Отримує всі налаштування"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            SELECT * FROM user_settings ORDER BY setting_name
        """)

        return [UserSetting.from_dict(dict(row)) for row in cursor.fetchall()]

    def update(self, setting: UserSetting) -> bool:
        """Оновлює налаштування"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            UPDATE user_settings 
            SET setting_value = ?, updated_at = CURRENT_TIMESTAMP
            WHERE setting_name = ?
        """, (setting.setting_value, setting.setting_name))

        conn.commit()
        return cursor.rowcount > 0

    def delete(self, name: str) -> bool:
        """Видаляє налаштування"""
        conn = self.db_manager.get_connection()
        cursor = conn.execute("""
            DELETE FROM user_settings WHERE setting_name = ?
        """, (name,))

        conn.commit()
        return cursor.rowcount > 0


