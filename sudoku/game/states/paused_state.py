import pygame
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WHITE, GRID_SIZE, CELL_SIZE, BLACK, BLUE, GRAY, WINDOW_SIZE

if TYPE_CHECKING:
    from ..game import Game


class PausedState(IGameState):
    """Стан гри на паузі"""

    def __init__(self):
        self.pause_buttons = {}
        self.button_width = 200
        self.button_height = 45
        self.button_spacing = 15
        self.button_border_radius = 10  # Радіус заокруглення кнопок

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Відображення градієнтного фону"""
        width, height = surface.get_size()

        # Кольори градієнту
        start_color = (240, 248, 255)  # Світло-блакитний
        end_color = (230, 230, 250)  # Лавандовий

        # Створення градієнту по вертикалі
        for y in range(height):
            # Розрахунок коефіцієнта інтерполяції (0.0 до 1.0)
            ratio = y / height

            # Інтерполяція кольору
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)

            # Малювання горизонтальної лінії
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

    def _initialize_pause_buttons(self, font):
        """Ініціалізує кнопки для стану паузи"""
        center_x = WINDOW_SIZE[0] // 2
        center_y = WINDOW_SIZE[1] // 2

        buttons_data = [
            ("resume", "Resume"),
            ("menu", "Main Menu")
        ]

        for i, (key, text) in enumerate(buttons_data):
            y = center_y - 50 + i * (self.button_height + self.button_spacing)
            rect = pygame.Rect(
                center_x - self.button_width // 2,
                y,
                self.button_width,
                self.button_height
            )
            text_surface = font.render(text, True, WHITE)
            self.pause_buttons[key] = (rect, text_surface)

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

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()

            # Ініціалізуємо кнопки, якщо вони ще не створені
            if not self.pause_buttons:
                self._initialize_pause_buttons(game.font)

            # Перевірка натискання на власні кнопки паузи
            for button_name, (rect, _) in self.pause_buttons.items():
                if rect.collidepoint(x, y):
                    if button_name == "resume":
                        game.resume_game()
                    elif button_name == "menu":
                        from .main_menu_state import MainMenuState
                        game.set_state(MainMenuState())
                    return

            # Перевірка натискання на кнопки через button_manager (якщо потрібно)
            clicked_button = game.button_manager.get_clicked_button(x, y)
            if clicked_button == "pause":
                game.resume_game()
            elif clicked_button == "menu":
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_SPACE:
                game.resume_game()
            elif event.key == pygame.K_ESCAPE:
                from .main_menu_state import MainMenuState
                game.set_state(MainMenuState())

    def update(self, game: 'Game') -> None:
        """Оновлення стану гри на паузі"""
        # Таймер не оновлюється під час паузи
        pass

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення стану гри на паузі"""
        # Відображення градієнтного фону замість білого
        self._draw_gradient_background(surface)

        # Відображення розмитої сітки
        game.renderer.draw_blurred_grid(surface)

        # Ініціалізуємо кнопки, якщо вони ще не створені
        if not self.pause_buttons:
            self._initialize_pause_buttons(game.font)

        # Напівпрозоре накладення для ефекту паузи
        overlay = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))  # Чорне напівпрозоре накладення
        surface.blit(overlay, (0, 0))

        # Заголовок паузи з заокругленим фоном
        pause_title = game.font.render("GAME PAUSED", True, WHITE)
        title_rect = pause_title.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 120))

        # Заокруглений фон під заголовок
        title_bg_rect = pygame.Rect(title_rect.x - 20, title_rect.y - 10,
                                    title_rect.width + 40, title_rect.height + 20)
        title_bg_surface = pygame.Surface((title_bg_rect.width, title_bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(title_bg_surface, (0, 0, 0, 150),
                         (0, 0, title_bg_rect.width, title_bg_rect.height),
                         border_radius=12)
        surface.blit(title_bg_surface, title_bg_rect)
        surface.blit(pause_title, title_rect)

        # Малювання заокруглених кнопок паузи
        for button_name, (rect, text_surface) in self.pause_buttons.items():
            if button_name == "resume":
                self._draw_rounded_button(surface, rect, BLUE, WHITE, text_surface)
            else:  # menu
                self._draw_rounded_button(surface, rect, GRAY, WHITE, text_surface)

        # Відображення таймеру (зупиненого)
        game.renderer.draw_timer(surface, game.timer.get_formatted_time())

        # Відображення кількості використаних підказок (нижче кнопок)
        hints_y = GRID_SIZE * CELL_SIZE + 130  # Збільшено відступ для розміщення під кнопками
        hints_text = game.small_font.render(
            f"Hints: {game.board.hints_used}/{game.board.max_hints}",
            True, BLACK
        )
        # Центруємо текст по горизонталі
        hints_rect = hints_text.get_rect()
        hints_rect.centerx = surface.get_width() // 2
        hints_rect.y = hints_y
        surface.blit(hints_text, hints_rect)