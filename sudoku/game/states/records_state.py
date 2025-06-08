import pygame
import sys
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

from .i_game_state import IGameState
from ...config import WINDOW_SIZE, WHITE, BLACK, BLUE, GRAY, GREEN
from ...models import Difficulty

if TYPE_CHECKING:
    from ..game import Game


class RecordsState(IGameState):
    """Стан показу таблиці рекордів"""

    def __init__(self):
        self.selected_difficulty: Optional[Difficulty] = None
        self.records = []
        self.personal_stats = {}
        self.scroll_offset = 0
        self.max_scroll = 0
        self.difficulty_buttons = {}
        self.back_button = None
        self.records_loaded = False

        # Налаштування інтерфейсу
        self.button_height = 40
        self.record_height = 30
        self.records_per_page = 15
        self.header_height = 150

        # RGB кольори для градієнтного фону
        self.background_color = (245, 245, 250)  # Світло-сірий
        self.gradient_color = (235, 235, 245)  # Трохи темніший сірий

        # Нові кольори для кнопок
        self.button_normal_color = (70, 130, 180)  # Steel Blue
        self.button_selected_color = (255, 165, 0)  # Orange
        self.button_back_color = (220, 20, 60)  # Crimson

    def _draw_gradient_background(self, surface):
        """Малює градієнтний фон"""
        width, height = surface.get_size()

        # Створюємо вертикальний градієнт
        for y in range(height):
            # Розраховуємо співвідношення для градієнта (0.0 до 1.0)
            ratio = y / height

            # Інтерполюємо кольори
            r = int(self.background_color[0] * (1 - ratio) + self.gradient_color[0] * ratio)
            g = int(self.background_color[1] * (1 - ratio) + self.gradient_color[1] * ratio)
            b = int(self.background_color[2] * (1 - ratio) + self.gradient_color[2] * ratio)

            # Малюємо горизонтальну лінію з поточним кольором
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    def _draw_rounded_rect(self, surface, color, rect, border_radius=10, border_width=0, border_color=BLACK):
        """Малює заокруглений прямокутник"""
        # Створюємо тимчасову поверхню з альфа-каналом
        temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Малюємо заокруглений прямокутник на тимчасовій поверхні
        pygame.draw.rect(temp_surface, color, (0, 0, rect.width, rect.height), border_radius=border_radius)

        # Якщо потрібна рамка
        if border_width > 0:
            pygame.draw.rect(temp_surface, border_color, (0, 0, rect.width, rect.height),
                             width=border_width, border_radius=border_radius)

        # Переносимо на основну поверхню
        surface.blit(temp_surface, rect.topleft)

    def _initialize_buttons(self, font, small_font):
        """Ініціалізує кнопки інтерфейсу"""
        # Кнопки фільтрів по складності
        button_width = 155
        button_spacing = 10

        # Всього кнопок: 3 рівні складності + 1 кнопка "All difficulty"
        total_buttons = len(Difficulty) + 1
        total_width = total_buttons * button_width + (total_buttons - 1) * button_spacing
        start_x = (WINDOW_SIZE[0] - total_width) // 2

        # Словник для перекладу назв рівнів складності
        difficulty_names = {
            Difficulty.EASY: "Easy",
            Difficulty.MEDIUM: "Medium",
            Difficulty.HARD: "Hard"
        }

        # Кнопка "Всі рівні" - перша зліва
        all_rect = pygame.Rect(start_x, 80, button_width, self.button_height)
        all_text = small_font.render("All difficulty", True, WHITE)
        self.difficulty_buttons[None] = (all_rect, all_text)

        # Кнопки рівнів складності
        for i, difficulty in enumerate(Difficulty):
            x = start_x + (i + 1) * (button_width + button_spacing)
            rect = pygame.Rect(x, 80, button_width, self.button_height)
            text = difficulty_names.get(difficulty, difficulty.name.capitalize())
            text_surface = small_font.render(text, True, WHITE)
            self.difficulty_buttons[difficulty] = (rect, text_surface)

        # Кнопка "Назад"
        self.back_button = (
            pygame.Rect(50, WINDOW_SIZE[1] - 60, 100, self.button_height),
            small_font.render("Back", True, WHITE)
        )

    def _load_records(self, game: 'Game'):
        """Завантажує рекорди з бази даних"""
        if not game.db_manager:
            self.records = []
            self.personal_stats = {}
            return

        try:
            # Завантажуємо рекорди
            self.records = game.get_leaderboard(self.selected_difficulty, limit=50)

            # Завантажуємо персональну статистику
            self.personal_stats = game.get_personal_stats()

            # Розраховуємо максимальний скрол
            visible_records = min(len(self.records), self.records_per_page)
            self.max_scroll = max(0, len(self.records) - visible_records)

        except Exception as e:
            print(f"Error loading records: {e}")
            self.records = []
            self.personal_stats = {}

    def _format_time(self, seconds: int) -> str:
        """Форматує час у читабельний вигляд"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _format_date(self, record) -> str:
        """Форматує дату у читабельний вигляд"""
        # Спочатку отримуємо дату з правильного атрибута
        date_value = None

        # Пробуємо різні атрибути в порядку пріоритету
        if hasattr(record, 'date_completed') and record.date_completed:
            date_value = record.date_completed
        elif hasattr(record, 'created_at') and record.created_at:
            date_value = record.created_at
        elif hasattr(record, 'date_played') and record.date_played:
            date_value = record.date_played
        elif hasattr(record, 'timestamp') and record.timestamp:
            date_value = record.timestamp

        if not date_value or str(date_value) == "None":
            return "--"

        try:
            # Якщо це вже об'єкт datetime
            if isinstance(date_value, datetime):
                return date_value.strftime("%d.%m.%Y %H:%M")

            # Якщо це рядок, пробуємо його парсити
            date_str = str(date_value)

            # ISO формат з T
            if 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Пробуємо стандартний формат SQLite
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    try:
                        # Без часу
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        # Якщо нічого не спрацювало, повертаємо скорочений рядок
                        return date_str[:16] if len(date_str) > 16 else date_str

            return date_obj.strftime("%d.%m.%Y %H:%M")

        except Exception as e:
            print(f"Error formatting date {date_value}: {e}")
            return str(date_value)[:16] if len(str(date_value)) > 16 else str(date_value)

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо потрібно
            if not self.difficulty_buttons:
                self._initialize_buttons(game.font, game.small_font)

            # Перевіряємо натискання на кнопки складності
            for difficulty, (rect, _) in self.difficulty_buttons.items():
                if rect.collidepoint(x, y):
                    if self.selected_difficulty != difficulty:
                        self.selected_difficulty = difficulty
                        self.records_loaded = False
                        self.scroll_offset = 0
                    break

            # Перевіряємо кнопку "Назад"
            if self.back_button and self.back_button[0].collidepoint(x, y):
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 1)

        elif event.type == pygame.MOUSEWHEEL:
            # Прокрутка колесом миші
            self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset - event.y))

    def update(self, game: 'Game') -> None:
        """Оновлення стану"""
        if not self.records_loaded:
            self._load_records(game)
            self.records_loaded = True

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення таблиці рекордів"""
        # Відображаємо градієнтний фон замість білого
        self._draw_gradient_background(surface)

        # Ініціалізуємо кнопки, якщо потрібно
        if not self.difficulty_buttons:
            self._initialize_buttons(game.font, game.small_font)

        # Заголовок
        title_text = game.font.render("RECORDS", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 30))
        surface.blit(title_text, title_rect)

        # Кнопки фільтрів з заокругленням та новими кольорами
        for difficulty, (rect, text_surface) in self.difficulty_buttons.items():
            # Вибір кольору кнопки
            if difficulty == self.selected_difficulty:
                color = self.button_selected_color  # Помаранчевий для вибраної кнопки
            else:
                color = self.button_normal_color  # Синій для звичайних кнопок

            # Малюємо заокруглену кнопку
            self._draw_rounded_rect(surface, color, rect, border_radius=12, border_width=2, border_color=BLACK)

            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

        # Персональна статистика
        if self.personal_stats and self.personal_stats.get('total_games', 0) > 0:
            stats_y = 130
            total_games = self.personal_stats.get('total_games', 0)
            avg_time = self.personal_stats.get('average_time', 0)
            stats_text = f"Your stats: Played games: {total_games}, \n" \
                         f"Average time: {self._format_time(avg_time)}"
            stats_surface = game.small_font.render(stats_text, True, BLACK)
            surface.blit(stats_surface, (50, stats_y))

        # Заголовки таблиці
        headers_y = self.header_height + 20
        header_font = game.small_font

        headers = ["#", "Time", "Difficulty", "Hints", "Date"]
        header_positions = [80, 120, 200, 340, 430]

        for i, (header, x_pos) in enumerate(zip(headers, header_positions)):
            header_surface = header_font.render(header, True, BLACK)
            surface.blit(header_surface, (x_pos, headers_y))

        # Лінія під заголовками
        pygame.draw.line(surface, GRAY, (50, headers_y + 25), (WINDOW_SIZE[0] - 50, headers_y + 25), 2)

        # Відображення рекордів
        if self.records:
            records_start_y = headers_y + 35

            for i, record in enumerate(self.records[self.scroll_offset:self.scroll_offset + self.records_per_page]):
                y_pos = records_start_y + i * self.record_height

                if i % 2 == 1:
                    row_rect = pygame.Rect(50, y_pos - 2, WINDOW_SIZE[0] - 100, self.record_height)
                    # Заокруглений фон для непарних рядків
                    self._draw_rounded_rect(surface, (245, 245, 245), row_rect, border_radius=8)

                # Номер у загальному рейтингу
                rank = self.scroll_offset + i + 1
                rank_text = header_font.render(str(rank), True, BLACK)
                surface.blit(rank_text, (header_positions[0], y_pos))

                # Час
                time_text = header_font.render(self._format_time(record.completion_time), True, BLACK)
                surface.blit(time_text, (header_positions[1], y_pos))

                # Рівень складності
                difficulty_names = {
                    Difficulty.EASY: "Easy",
                    Difficulty.MEDIUM: "Medium",
                    Difficulty.HARD: "Hard"
                }
                diff_text = header_font.render(
                    difficulty_names.get(record.difficulty, record.difficulty.name.capitalize()),
                    True, BLACK
                )
                surface.blit(diff_text, (header_positions[2], y_pos))

                # Кількість підказок
                hints_text = header_font.render(str(record.hints_used), True, BLACK)
                surface.blit(hints_text, (header_positions[3], y_pos))

                # Дата - використовуємо виправлену функцію
                date_text = header_font.render(self._format_date(record), True, BLACK)
                surface.blit(date_text, (header_positions[4], y_pos))

        else:
            # Повідомлення про відсутність рекордів
            no_records_text = game.font.render("No records yet", True, GRAY)
            no_records_rect = no_records_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            surface.blit(no_records_text, no_records_rect)

        # Кнопка "Назад" з заокругленням та новим кольором
        if self.back_button:
            rect, text_surface = self.back_button
            self._draw_rounded_rect(surface, self.button_back_color, rect, border_radius=12, border_width=2,
                                    border_color=BLACK)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

        # Індикатор прокрутки, якщо потрібно
        if len(self.records) > self.records_per_page:
            scroll_info = game.small_font.render(
                f"Entries {self.scroll_offset + 1}-{min(self.scroll_offset + self.records_per_page, len(self.records))} з {len(self.records)}",
                True, GRAY
            )
            surface.blit(scroll_info, (WINDOW_SIZE[0] - 250, WINDOW_SIZE[1] - 30))