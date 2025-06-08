import pygame
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WINDOW_SIZE, WHITE, BLUE, BLACK, GRAY
from ...models import Difficulty

if TYPE_CHECKING:
    from ..game import Game


class DifficultySelectState(IGameState):
    """Стан вибору складності"""

    def __init__(self):
        self.difficulty_buttons = {}
        self.back_button = None
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20

        # RGB кольори для градієнтного фону
        self.background_color = (250, 250, 255)  # Дуже світло-блакитний
        self.gradient_color = (240, 248, 255)  # Світло-блакитний

        # Налаштування для заокруглених кнопок
        self.button_border_radius = 15

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

    def _draw_rounded_button(self, surface, rect, color, border_color, text_surface):
        """Малює заокруглену кнопку з текстом"""
        # Створюємо поверхню для заокругленого фону кнопки
        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (*color, 200),
                         (0, 0, rect.width, rect.height),
                         border_radius=self.button_border_radius)
        surface.blit(button_surface, rect)

        # Малюємо заокруглену границю
        border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, border_color,
                         (0, 0, rect.width, rect.height),
                         width=2, border_radius=self.button_border_radius)
        surface.blit(border_surface, rect)

        # Центруємо текст на кнопці
        text_rect = text_surface.get_rect(center=rect.center)
        surface.blit(text_surface, text_rect)

    def _initialize_difficulty_buttons(self, font):
        """Ініціалізує кнопки вибору складності"""
        center_x = WINDOW_SIZE[0] // 2
        start_y = WINDOW_SIZE[1] // 2 - 80

        difficulties = [
            (Difficulty.EASY, "Easy"),
            (Difficulty.MEDIUM, "Medium"),
            (Difficulty.HARD, "Hard")
        ]

        for i, (difficulty, text) in enumerate(difficulties):
            y = start_y + i * (self.button_height + self.button_spacing)
            rect = pygame.Rect(
                center_x - self.button_width // 2,
                y,
                self.button_width,
                self.button_height
            )
            text_surface = font.render(text, True, WHITE)
            self.difficulty_buttons[difficulty] = (rect, text_surface)

        # Кнопка повернення
        back_y = start_y + len(difficulties) * (self.button_height + self.button_spacing) + 20
        back_rect = pygame.Rect(
            center_x - 100,
            back_y,
            200,
            40
        )
        back_text = font.render("Back", True, WHITE)
        self.back_button = (back_rect, back_text)

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо вони ще не створені
            if not self.difficulty_buttons:
                self._initialize_difficulty_buttons(game.font)

            # Перевірка натискання на кнопки складності
            for difficulty, (rect, _) in self.difficulty_buttons.items():
                if rect.collidepoint(x, y):
                    game.difficulty = difficulty
                    game.new_game()
                    # Імпортуємо тут, щоб уникнути циркулярного імпорту
                    from .playing_state import PlayingState
                    game.set_state(PlayingState())
                    return

            # Перевірка натискання на кнопку "Назад"
            if self.back_button and self.back_button[0].collidepoint(x, y):
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

    def update(self, game: 'Game') -> None:
        """Оновлення стану вибору складності"""
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення меню вибору складності"""
        # Відображаємо градієнтний фон замість білого
        self._draw_gradient_background(surface)

        # Ініціалізуємо кнопки, якщо вони ще не створені
        if not self.difficulty_buttons:
            self._initialize_difficulty_buttons(game.font)

        # Заголовок
        title_text = game.font.render("Choose difficulty", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 150))
        surface.blit(title_text, title_rect)

        # Малювання кнопок складності з заокругленими кутами
        difficulty_colors = {
            Difficulty.EASY: (34, 139, 34),  # Зелений
            Difficulty.MEDIUM: (255, 165, 0),  # Помаранчевий
            Difficulty.HARD: (220, 20, 60)  # Червоний
        }

        for difficulty, (rect, text_surface) in self.difficulty_buttons.items():
            color = difficulty_colors.get(difficulty, BLUE)
            self._draw_rounded_button(surface, rect, color, BLACK, text_surface)

        # Малювання кнопки "Назад" з заокругленими кутами
        if self.back_button:
            rect, text_surface = self.back_button
            self._draw_rounded_button(surface, rect, GRAY, BLACK, text_surface)