"""
Основний модуль гри з інтеграцією бази даних
"""
import os

import pygame
from typing import Optional, Tuple
import logging

from sudoku.game.states.main_menu_state import MainMenuState
from ..config import WINDOW_SIZE, GRID_SIZE
from ..models import Difficulty
from ..core import SudokuGenerator, SudokuBoard
from ..ui import SudokuRenderer, ButtonManager
from .states.game_over_state import GameOverState
from .states.i_game_state import IGameState
from .states.paused_state import PausedState
from .states.playing_state import PlayingState
from .timer import GameTimer
from .database_integration import GameDatabaseManager


class Game:
    """Основний клас гри з підтримкою бази даних"""
    def __init__(self, db_path: Optional[str] = None):
        pygame.init()
        self.window_size = WINDOW_SIZE
        self.surface = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Sudoku')

        # Ініціалізація бази даних
        try:
            self.db_manager = GameDatabaseManager(db_path)
            logging.info("Database integration initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize database: {e}")
            self.db_manager = None

        # Ініціалізація шрифтів

        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, 'alk-life-webfont.ttf')

        self.font = pygame.font.Font(font_path, 32)
        self.small_font = pygame.font.Font(font_path, 20)

        # Ініціалізація компонентів гри
        self.generator = SudokuGenerator()
        self.board = SudokuBoard(self.generator)
        self.renderer = SudokuRenderer(self.font, self.small_font)
        self.button_manager = ButtonManager(self.small_font)
        self.timer = GameTimer()

        # Завантаження налаштувань з бази даних
        self._load_user_settings()

        # Стан гри
        self.selected_cell: Optional[Tuple[int, int]] = None
        self.difficulty = self._get_preferred_difficulty()

        # Починаємо з головного меню
        self.state: IGameState = MainMenuState()

        # Прапорець для перевірки, чи була ініціалізована гра
        self.game_initialized = False

    def _load_user_settings(self):
        """Завантажує налаштування користувача з бази даних"""
        if self.db_manager:
            try:
                # Завантажуємо максимальну кількість підказок
                max_hints = self.db_manager.get_max_hints()
                # Тут можна встановити це значення в board, коли він буде ініціалізований

                # Завантажуємо інші налаштування за потреби
                logging.info("User settings loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load user settings: {e}")

    def _get_preferred_difficulty(self) -> Difficulty:
        """Отримує переважний рівень складності з бази даних"""
        if self.db_manager:
            try:
                pref_difficulty = self.db_manager.get_user_setting('preferred_difficulty')
                if pref_difficulty:
                    return Difficulty[pref_difficulty]
            except Exception as e:
                logging.error(f"Failed to get preferred difficulty: {e}")

        return Difficulty.MEDIUM  # За замовчуванням

    def _initialize_game_ui(self):
        """Ініціалізує елементи ігрового інтерфейсу"""
        if not self.game_initialized:
            self.button_manager.initialize_buttons()

            # Встановлюємо максимальну кількість підказок з бази даних
            if self.db_manager:
                max_hints = self.db_manager.get_max_hints()
                self.board.max_hints = max_hints

            self.game_initialized = True

    def new_game(self):
        """Створює нову гру"""
        self._initialize_game_ui()
        self.board.initialize(self.difficulty)
        self.selected_cell = None
        self.timer.reset()

    def save_current_game(self) -> bool:
        """Зберігає поточну гру в базу даних"""
        if not self.db_manager:
            logging.warning("Database not available for saving game")
            return False

        try:
            elapsed_time_seconds = self.timer.get_time() // 1000
            return self.db_manager.save_current_game(
                self.difficulty,
                self.board.grid,
                self.board.solution,
                elapsed_time_seconds,
                self.board.hints_used
            )
        except Exception as e:
            logging.error(f"Failed to save current game: {e}")
            return False

    def load_saved_game(self, game_id: Optional[int] = None):
        """Завантажує збережену гру з бази даних"""
        if not self.db_manager:
            logging.warning("Database not available for loading game")
            return False

        try:
            if game_id:
                saved_game = self.db_manager.saved_game_service.load_game(game_id)
            else:
                saved_game = self.db_manager.load_latest_game()

            if saved_game:
                self.difficulty = saved_game.difficulty

                # Відновлюємо стан дошки
                self.board.difficulty = saved_game.difficulty
                self.board.solution = saved_game.solution
                self.board.hints_used = saved_game.hints_used

                # Конвертуємо збережений стан назад у клітинки
                from ..models import Cell
                self.board.grid = []
                for row_data in saved_game.current_state:
                    row = []
                    for cell_data in row_data:
                        cell = Cell.from_dict(cell_data)
                        row.append(cell)
                    self.board.grid.append(row)

                # Відновлюємо таймер
                self.timer.elapsed_time = saved_game.elapsed_time * 1000  # Конвертуємо в мс
                self.timer.start()

                # Переходимо до стану гри
                self.set_state(PlayingState())

                logging.info(f"Game loaded successfully: {saved_game.id}")
                return True
            else:
                logging.info("No saved game found")
                return False

        except Exception as e:
            logging.error(f"Failed to load saved game: {e}")
            return False

    def complete_game(self):
        """Викликається при завершенні гри для збереження результату"""
        if not self.db_manager:
            logging.warning("Database not available for saving game record")
            return

        try:
            completion_time_seconds = self.timer.get_time() // 1000
            success = self.db_manager.save_game_record(
                self.difficulty,
                completion_time_seconds,
                self.board.hints_used
            )

            if success:
                logging.info("Game record saved successfully")
            else:
                logging.warning("Failed to save game record")

        except Exception as e:
            logging.error(f"Error saving game record: {e}")

    def get_leaderboard(self, difficulty: Optional[Difficulty] = None, limit: int = 10):
        """Отримує таблицю лідерів"""
        if not self.db_manager:
            return []

        return self.db_manager.get_leaderboard(difficulty, limit)

    def get_personal_stats(self):
        """Отримує персональну статистику"""
        if not self.db_manager:
            return {}

        return self.db_manager.get_personal_stats()

    def has_saved_games(self) -> bool:
        """Перевіряє, чи є збережені ігри"""
        if not self.db_manager:
            return False

        return self.db_manager.has_saved_games()

    def pause_game(self):
        """Ставить гру на паузу"""
        if isinstance(self.state, PlayingState):
            self.timer.pause()
            self.state = PausedState()
            self.button_manager.update_pause_button("Continue")


    def resume_game(self):
        """Відновлює гру після паузи"""
        if isinstance(self.state, PausedState):
            self.timer.resume()
            self.state = PlayingState()
            self.button_manager.update_pause_button("Pause")

    def select_cell(self, row: int, col: int):
        """Обирає клітинку"""
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            self.selected_cell = (row, col)

    def use_hint(self):
        """Використовує підказку"""
        hint = self.board.get_hint()
        if hint:
            row, col, value = hint
            self.board.set_value(row, col, value)
            self.selected_cell = (row, col)

            # Перевірка на завершення гри після використання підказки
            if self.board.is_complete():
                self.timer.pause()
                self.complete_game()  # Зберігаємо результат
                self.state = GameOverState()

    def set_state(self, new_state: IGameState):
        """Встановлює новий стан гри"""
        if isinstance(new_state, GameOverState):
            self.timer.pause()
            self.complete_game()  # Зберігаємо результат при завершенні гри
        self.state = new_state

    def run(self):
        """Головний цикл гри"""
        running = True
        clock = pygame.time.Clock()

        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    else:
                        self.state.handle_event(event, self)

                self.state.update(self)
                self.state.render(self.surface, self)

                pygame.display.flip()
                clock.tick(30)
        finally:
            # Закриваємо базу даних при виході
            if self.db_manager:
                self.db_manager.close()
            pygame.quit()


# Приклад використання:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    game = Game()

    # Або з кастомним шляхом:
    # game = Game(db_path="custom_path/sudoku.db")

    game.run()