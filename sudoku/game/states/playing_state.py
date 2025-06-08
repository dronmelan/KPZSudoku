import pygame
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import GRID_SIZE, CELL_SIZE, WHITE, BLACK

if TYPE_CHECKING:
    from ..game import Game


class PlayingState(IGameState):
    """Стан гри під час гри"""

    def __init__(self):
        # RGB кольори для градієнтного фону
        self.background_color = (240, 248, 255)  # Світло-блакитний
        self.gradient_color = (230, 230, 250)  # Світло-лавандовий

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

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Перевірка натискання на кнопки
            clicked_button = game.button_manager.get_clicked_button(x, y)
            if clicked_button:
                self._handle_button_click(clicked_button, game)
                return

            # Вибір клітинки - використовуємо метод renderer для правильного визначення координат
            cell_coords = game.renderer.get_cell_from_pos((x, y))
            if cell_coords:
                row, col = cell_coords
                game.select_cell(row, col)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())
            else:
                self._handle_key_press(event.key, game)

    def _handle_button_click(self, button_name: str, game: 'Game') -> None:
        """Обробка натискання кнопок"""
        if button_name == "new_game":
            from .difficulty_select_state import DifficultySelectState
            game.set_state(DifficultySelectState())
        elif button_name == "hint":
            game.use_hint()
        elif button_name == "auto_notes":
            game.board.auto_notes()
        elif button_name == "pause":
            game.pause_game()
        elif button_name == "menu":
            from .main_menu_state import MainMenuState
            game.set_state(MainMenuState())

    def _handle_key_press(self, key: int, game: 'Game') -> None:
        """Обробка натискання клавіш"""
        if game.selected_cell:
            row, col = game.selected_cell

            if key == pygame.K_BACKSPACE or key == pygame.K_DELETE or key == pygame.K_0:
                game.board.clear_cell(row, col)
            elif pygame.K_1 <= key <= pygame.K_9:
                number = key - pygame.K_0

                # Якщо натиснуто Shift, додаємо/видаляємо замітку
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    game.board.toggle_note(row, col, number)
                else:
                    game.board.set_value(row, col, number)

                    # Перевірка на завершення гри
                    if game.board.is_complete():
                        from .game_over_state import GameOverState
                        game.set_state(GameOverState())

            # Навігація стрілками
            elif key == pygame.K_UP and row > 0:
                game.select_cell(row - 1, col)
            elif key == pygame.K_DOWN and row < GRID_SIZE - 1:
                game.select_cell(row + 1, col)
            elif key == pygame.K_LEFT and col > 0:
                game.select_cell(row, col - 1)
            elif key == pygame.K_RIGHT and col < GRID_SIZE - 1:
                game.select_cell(row, col + 1)

        # Гарячі клавіші
        if key == pygame.K_h:  # Підказка
            game.use_hint()
        elif key == pygame.K_a:  # Автозаповнення заміток
            game.board.auto_notes()
        elif key == pygame.K_p or key == pygame.K_SPACE:  # Пауза
            game.pause_game()

    def update(self, game: 'Game') -> None:
        """Оновлення стану гри"""
        # Оновлюємо таймер тільки якщо гра не на паузі
        game.timer.update()

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення стану гри"""
        # Відображаємо градієнтний фон замість білого
        self._draw_gradient_background(surface)

        # Відображення сітки
        game.renderer.draw_grid(surface, game.board.grid, game.selected_cell)

        # Використовуємо новий метод для малювання заокруглених кнопок
        game.button_manager.draw_rounded_buttons(surface)

        # Відображення інформації нижче кнопок
        info_y = GRID_SIZE * CELL_SIZE + 100  # Позиція для інформаційного рядка

        # Відображення таймеру (ліворуч)
        timer_text = game.small_font.render(
            f"Time: {game.timer.get_formatted_time()}",
            True, BLACK
        )
        timer_rect = timer_text.get_rect()
        timer_rect.x = 20  # Відступ зліва
        timer_rect.y = info_y
        surface.blit(timer_text, timer_rect)

        # Відображення кількості використаних підказок (праворуч)
        hints_text = game.small_font.render(
            f"Hints: {game.board.hints_used}/{game.board.max_hints}",
            True, BLACK
        )
        hints_rect = hints_text.get_rect()
        hints_rect.x = surface.get_width() - hints_rect.width - 20  # Відступ справа
        hints_rect.y = info_y
        surface.blit(hints_text, hints_rect)