"""
Менеджер бази даних для ініціалізації та управління з'єднанням
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
import logging


class DatabaseManager:
    """Клас для управління базою даних SQLite"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Створюємо папку для даних гри
            data_dir = Path.home() / '.sudoku_game'
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / 'sudoku.db')

        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

        # Налаштування логування
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def connect(self) -> sqlite3.Connection:
        """Створює з'єднання з базою даних"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Для роботи з рядками як з словниками
            self.logger.info(f"Connected to database: {self.db_path}")
            return self.connection
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {e}")
            raise

    def disconnect(self):
        """Закриває з'єднання з базою даних"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.logger.info("Database connection closed")

    def get_connection(self) -> sqlite3.Connection:
        """Повертає поточне з'єднання або створює нове"""
        if self.connection is None:
            return self.connect()
        return self.connection

    def initialize_database(self):
        """Ініціалізує базу даних, створюючи необхідні таблиці"""
        conn = self.get_connection()

        try:
            # SQL скрипт для створення таблиць
            create_tables_sql = """
            -- Таблиця для рекордів завершених ігор
            CREATE TABLE IF NOT EXISTS game_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                difficulty TEXT NOT NULL CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')),
                completion_time INTEGER NOT NULL,
                hints_used INTEGER NOT NULL DEFAULT 0,
                score INTEGER NOT NULL DEFAULT 0,
                date_completed TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Таблиця для збережених ігор
            CREATE TABLE IF NOT EXISTS saved_games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                difficulty TEXT NOT NULL CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')),
                current_state TEXT NOT NULL,
                solution TEXT NOT NULL,
                elapsed_time INTEGER NOT NULL DEFAULT 0,
                hints_used INTEGER NOT NULL DEFAULT 0,
                date_saved TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Таблиця для налаштувань користувача
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_name TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            
            -- Індекси для оптимізації запитів
            CREATE INDEX IF NOT EXISTS idx_game_records_difficulty ON game_records(difficulty);
            CREATE INDEX IF NOT EXISTS idx_game_records_score ON game_records(score DESC);
            CREATE INDEX IF NOT EXISTS idx_game_records_date ON game_records(date_completed);
            CREATE INDEX IF NOT EXISTS idx_saved_games_date ON saved_games(date_saved DESC);
            CREATE INDEX IF NOT EXISTS idx_user_settings_name ON user_settings(setting_name);
            """

            conn.executescript(create_tables_sql)
            conn.commit()

            self.logger.info("Database tables created successfully")

            # Ініціалізуємо базові налаштування
            self._initialize_default_settings(conn)

        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {e}")
            conn.rollback()
            raise

    def _initialize_default_settings(self, conn: sqlite3.Connection):
        """Ініціалізує базові налаштування користувача"""
        default_settings = [
            ('theme', 'light'),
            ('sound_enabled', 'true'),
            ('auto_notes', 'false'),
            ('highlight_conflicts', 'true'),
            ('show_timer', 'true'),
            ('max_hints', '5')
        ]

        for setting_name, setting_value in default_settings:
            conn.execute("""
                INSERT OR IGNORE INTO user_settings (setting_name, setting_value)
                VALUES (?, ?)
            """, (setting_name, setting_value))

        conn.commit()
        self.logger.info("Default settings initialized")

    def backup_database(self, backup_path: str):
        """Створює резервну копію бази даних"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            raise

    def __enter__(self):
        """Контекстний менеджер - вхід"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстний менеджер - вихід"""
        self.disconnect()