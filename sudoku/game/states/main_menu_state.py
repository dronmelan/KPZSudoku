import pygame
import sys
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WINDOW_SIZE, WHITE, BLACK, BLUE, GRAY

if TYPE_CHECKING:
    from ..game import Game


class MainMenuState(IGameState):
    """Стан головного меню"""

    def __init__(self):
        self.menu_buttons = {}
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20
        self.button_border_radius = 10  # Радіус заокруглення кнопок
        # RGB колір для фону (можете змінити на будь-який колір)
        self.background_color = (45, 52, 54)  # Темно-сірий
        self.gradient_color = (99, 110, 114)  # Світліший сірий для градієнта

    def _draw_gradient_background(self, surface):
        """Малює градієнтний фон"""
        width, height = WINDOW_SIZE

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

    def _initialize_menu_buttons(self, font):
        """Ініціалізує кнопки головного меню"""
        center_x = WINDOW_SIZE[0] // 2
        start_y = WINDOW_SIZE[1] // 2 - 100

        buttons_data = [
            ("play", "Play"),
            ("records", "Records"),
            ("exit", "Quit")
        ]

        for i, (key, text) in enumerate(buttons_data):
            y = start_y + i * (self.button_height + self.button_spacing)
            rect = pygame.Rect(
                center_x - self.button_width // 2,
                y,
                self.button_width,
                self.button_height
            )
            text_surface = font.render(text, True, WHITE)
            self.menu_buttons[key] = (rect, text_surface)

    def _draw_rounded_rect(self, surface, color, rect, border_radius):
        """Малює заокруглений прямокутник"""
        # Створюємо тимчасову поверхню для заокругленого прямокутника
        rounded_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(rounded_surface, color, (0, 0, rect.width, rect.height), border_radius=border_radius)
        surface.blit(rounded_surface, rect)

    def _draw_rounded_rect_outline(self, surface, color, rect, border_radius, width):
        """Малює контур заокругленого прямокутника"""
        # Малюємо заповнений заокруглений прямокутник з кольором контуру
        self._draw_rounded_rect(surface, color, rect, border_radius)

        # Малюємо внутрішній прямокутник з прозорим кольором, щоб залишити тільки контур
        inner_rect = pygame.Rect(rect.x + width, rect.y + width,
                                 rect.width - 2 * width, rect.height - 2 * width)
        if inner_rect.width > 0 and inner_rect.height > 0:
            inner_surface = pygame.Surface((inner_rect.width, inner_rect.height), pygame.SRCALPHA)
            inner_surface.fill((0, 0, 0, 0))  # Прозорий
            surface.blit(inner_surface, inner_rect)

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо вони ще не створені
            if not self.menu_buttons:
                self._initialize_menu_buttons(game.font)

            for button_name, (rect, _) in self.menu_buttons.items():
                if rect.collidepoint(x, y):
                    self._handle_menu_click(button_name, game)
                    break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def _handle_menu_click(self, button_name: str, game: 'Game') -> None:
        """Обробка натiskання кнопок меню"""
        if button_name == "play":
            # Імпортуємо тут, щоб уникнути циркулярного імпорту
            from .difficulty_select_state import DifficultySelectState
            game.set_state(DifficultySelectState())
        elif button_name == "continue":
            # Перевіряємо, чи є збережені ігри
            if game.has_saved_games():
                # Завантажуємо останню збережену гру
                if game.load_saved_game():
                    print("Game successfully loaded")
                else:
                    print("Game loading error")
            else:
                print("No saved games")
        elif button_name == "records":
            # Активуємо показ таблиці рекордів
            from .records_state import RecordsState
            game.set_state(RecordsState())
        elif button_name == "exit":
            pygame.quit()
            sys.exit()

    def update(self, game: 'Game') -> None:
        """Оновлення стану меню"""
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення головного меню"""
        # Відображаємо градієнтний фон
        self._draw_gradient_background(surface)

        # Ініціалізуємо кнопки, якщо вони ще не створені
        if not self.menu_buttons:
            self._initialize_menu_buttons(game.font)

        # Заголовок з напівпрозорим фоном для кращої читабельності
        title_text = game.font.render("SUDOKU", True, WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 100))

        # Додаємо напівпрозорий заокруглений фон під заголовок
        title_bg_rect = pygame.Rect(title_rect.x - 10, title_rect.y - 5,
                                    title_rect.width + 20, title_rect.height + 10)
        title_bg_surface = pygame.Surface((title_bg_rect.width, title_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(title_bg_surface, (0, 0, 0, 100),
                         (0, 0, title_bg_rect.width, title_bg_rect.height),
                         border_radius=8)
        surface.blit(title_bg_surface, title_bg_rect)

        surface.blit(title_text, title_rect)

        # Малювання заокруглених кнопок меню
        for button_name, (rect, text_surface) in self.menu_buttons.items():
            # Створюємо напівпрозору кнопку з заокругленими краями
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, (*BLUE, 180),
                             (0, 0, rect.width, rect.height),
                             border_radius=self.button_border_radius)
            surface.blit(button_surface, rect)

            # Білі заокруглені границі
            border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, WHITE,
                             (0, 0, rect.width, rect.height),
                             width=2, border_radius=self.button_border_radius)
            surface.blit(border_surface, rect)

            # Центрування тексту на кнопці
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)