import pygame
import sys
from typing import TYPE_CHECKING

from .i_game_state import IGameState
from ...config import WHITE

if TYPE_CHECKING:
    from ..game import Game


class GameOverState(IGameState):
    """Стан гри після завершення"""

    def __init__(self):
        """Ініціалізація стану з перевіркою pygame"""
        try:
            # Перевірка, чи ініціалізований pygame
            if not pygame.get_init():
                pygame.init()
        except Exception as e:
            print(f"Помилка ініціалізації pygame в GameOverState: {e}")
            raise

    def _draw_gradient_background(self, surface: pygame.Surface) -> None:
        """Відображення градієнтного фону з обробкою помилок"""
        try:
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

        except Exception as e:
            print(f"Помилка при малюванні градієнту: {e}")
            # Fallback до білого фону
            surface.fill(WHITE)

    def handle_event(self, event: pygame.event.Event, game: 'Game') -> None:
        """Обробка подій з перевіркою помилок"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    try:
                        from .difficulty_select_state import DifficultySelectState
                        game.set_state(DifficultySelectState())
                    except ImportError as e:
                        print(f"Помилка імпорту DifficultySelectState: {e}")
                        # Fallback до головного меню
                        from .main_menu_state import MainMenuState
                        game.set_state(MainMenuState())
                elif event.key == pygame.K_ESCAPE:
                    try:
                        from .main_menu_state import MainMenuState
                        game.set_state(MainMenuState())
                    except ImportError as e:
                        print(f"Помилка імпорту MainMenuState: {e}")
                        # Завершення гри
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Можна додати кнопки для нової гри або повернення в меню
                pass
        except Exception as e:
            print(f"Помилка в handle_event: {e}")

    def update(self, game: 'Game') -> None:
        """Оновлення стану"""
        try:
            # Таймер не оновлюється після завершення гри
            pass
        except Exception as e:
            print(f"Помилка в update: {e}")

    def render(self, surface: pygame.Surface, game: 'Game') -> None:
        """Відображення з обробкою помилок"""
        try:
            # Перевірка валідності surface
            if not surface or not hasattr(surface, 'get_size'):
                print("Помилка: неправильний surface")
                return

            # Відображення градієнтного фону замість білого
            self._draw_gradient_background(surface)

            # Перевірка наявності renderer
            if not hasattr(game, 'renderer') or game.renderer is None:
                print("Помилка: renderer не ініціалізований")
                return

            # Відображаємо ігрову дошку
            if hasattr(game, 'board') and game.board:
                try:
                    game.renderer.draw_grid(surface, game.board.grid, None)
                except Exception as e:
                    print(f"Помилка відображення дошки: {e}")

            # Відображення кнопок з перевіркою
            if hasattr(game, 'button_manager') and game.button_manager:
                try:
                    # Перевіряємо чи buttons не порожній та правильно структурований
                    if hasattr(game.button_manager, 'buttons') and game.button_manager.buttons:
                        # Додаткова перевірка структури buttons
                        valid_buttons = {}
                        for key, value in game.button_manager.buttons.items():
                            if isinstance(value, (list, tuple)) and len(value) > 0:
                                valid_buttons[key] = value

                        if valid_buttons:
                            game.renderer.draw_buttons(surface, valid_buttons)
                except Exception as e:
                    print(f"Помилка відображення кнопок: {e}")

            # Відображення фінального часу
            if hasattr(game, 'timer') and game.timer:
                try:
                    game.renderer.draw_timer(surface, game.timer.get_formatted_time())
                except Exception as e:
                    print(f"Помилка відображення таймера: {e}")

            # Потім відображаємо повідомлення про завершення
            try:
                game.renderer.draw_game_over(surface)
            except Exception as e:
                print(f"Помилка відображення game over: {e}")
                # Fallback відображення
                try:
                    font = pygame.font.Font(None, 48)
                    text = font.render("GAME OVER", True, (255, 0, 0))
                    text_rect = text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
                    surface.blit(text, text_rect)

                    font_small = pygame.font.Font(None, 24)
                    instruction = font_small.render("Press N for new game or ESC for menu", True, (0, 0, 0))
                    instr_rect = instruction.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 50))
                    surface.blit(instruction, instr_rect)
                except:
                    pass

        except AttributeError as e:
            print(f"Помилка атрибуту в render: {e}")
        except Exception as e:
            print(f"Загальна помилка в render: {e}")
            # Мінімальне відображення
            try:
                surface.fill(WHITE)
                font = pygame.font.Font(None, 36)
                text = font.render("Game Over", True, (0, 0, 0))
                surface.blit(text, (surface.get_width() // 2 - text.get_width() // 2,
                                    surface.get_height() // 2 - text.get_height() // 2))
            except:
                pass