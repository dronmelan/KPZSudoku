import pygame
from typing import Dict, Tuple

from ..config import GRID_SIZE, CELL_SIZE, WHITE, BLACK


class ButtonManager:
    """Клас для управління кнопками інтерфейсу з підтримкою заокруглених кнопок"""

    def __init__(self, small_font: pygame.font.Font):
        self.small_font = small_font
        self.buttons: Dict[str, Dict] = {}  # Змінили на Dict для кращої структури
        self.button_height = 35
        self.button_y = GRID_SIZE * CELL_SIZE + 50  # Рядок для кнопок
        # Зберігаємо оригінальні позиції кнопок
        self.button_positions: Dict[str, Tuple[int, int, int]] = {}  # x, y, width

        # Кольори для кнопок
        self.button_colors = {
            "new_game": (70, 130, 180),  # Steel Blue
            "hint": (255, 140, 0),  # Dark Orange
            "pause": (220, 20, 60),  # Crimson
            "auto_notes": (34, 139, 34),  # Forest Green
            "menu": (128, 128, 128)  # Gray
        }

    def change_font(self, new_font: pygame.font.Font):
        """Змінює шрифт кнопок та перерендерює їх"""
        self.small_font = new_font
        self.refresh_buttons()

    def refresh_buttons(self):
        """Перерендерює всі кнопки з поточним шрифтом"""
        if not self.button_positions:
            return

        # Перерендерюємо кожну кнопку
        for button_name, (x, y, width) in self.button_positions.items():
            if button_name == "new_game":
                text = "New game"
            elif button_name == "hint":
                text = "Hint"
            elif button_name == "pause":
                # Зберігаємо поточний текст паузи
                current_text = self.buttons.get("pause", {}).get("text", "Pause")
                text = current_text
            elif button_name == "auto_notes":
                text = "Auto"
            elif button_name == "menu":
                text = "Menu"
            else:
                continue

            button_rect = pygame.Rect(x, y, width, self.button_height)
            self.buttons[button_name] = {
                "rect": button_rect,
                "text": text,
                "color": self.button_colors.get(button_name, (70, 130, 180))
            }

    def initialize_buttons(self):
        """Ініціалізує кнопки інтерфейсу в один рядок"""
        margin_left = 10
        spacing = 10
        current_x = margin_left
        y = self.button_y

        # Кнопка нової гри (тепер веде до вибору складності)
        new_game_width = 120
        new_game_rect = pygame.Rect(current_x, y, new_game_width, self.button_height)
        self.buttons["new_game"] = {
            "rect": new_game_rect,
            "text": "New game",
            "color": self.button_colors["new_game"]
        }
        self.button_positions["new_game"] = (current_x, y, new_game_width)
        current_x += new_game_width + spacing

        # Кнопка підказки
        hint_width = 120
        hint_rect = pygame.Rect(current_x, y, hint_width, self.button_height)
        self.buttons["hint"] = {
            "rect": hint_rect,
            "text": "Hint",
            "color": self.button_colors["hint"]
        }
        self.button_positions["hint"] = (current_x, y, hint_width)
        current_x += hint_width + spacing

        # Кнопка паузи - зберігаємо її позицію та ширину
        pause_width = 120  # Збільшуємо ширину для тексту "Продовжити"
        pause_rect = pygame.Rect(current_x, y, pause_width, self.button_height)
        self.buttons["pause"] = {
            "rect": pause_rect,
            "text": "Pause",
            "color": self.button_colors["pause"]
        }
        self.button_positions["pause"] = (current_x, y, pause_width)
        current_x += pause_width + spacing

        # Кнопка авто-заміток
        auto_notes_width = 120
        auto_notes_rect = pygame.Rect(current_x, y, auto_notes_width, self.button_height)
        self.buttons["auto_notes"] = {
            "rect": auto_notes_rect,
            "text": "Auto",
            "color": self.button_colors["auto_notes"]
        }
        self.button_positions["auto_notes"] = (current_x, y, auto_notes_width)
        current_x += auto_notes_width + spacing

        # Кнопка меню (замість кнопки складності)
        menu_width = 120
        menu_rect = pygame.Rect(current_x, y, menu_width, self.button_height)
        self.buttons["menu"] = {
            "rect": menu_rect,
            "text": "Menu",
            "color": self.button_colors["menu"]
        }
        self.button_positions["menu"] = (current_x, y, menu_width)

    def update_pause_button(self, text: str):
        """Оновлює текст кнопки паузи, зберігаючи її позицію"""
        if "pause" in self.button_positions:
            x, y, width = self.button_positions["pause"]
            pause_rect = pygame.Rect(x, y, width, self.button_height)
            self.buttons["pause"] = {
                "rect": pause_rect,
                "text": text,
                "color": self.button_colors["pause"]
            }

    def get_clicked_button(self, x: int, y: int) -> str:
        """Повертає назву кнопки, на яку натиснули, або пусту строку"""
        for button_name, button_data in self.buttons.items():
            if button_data["rect"].collidepoint(x, y):
                return button_name
        return ""

    def draw_rounded_buttons(self, surface: pygame.Surface):
        """Малює всі кнопки з заокругленими краями"""
        for button_name, button_data in self.buttons.items():
            rect = button_data["rect"]
            text = button_data["text"]
            color = button_data["color"]

            # Малюємо заокруглену кнопку з тінню
            self._draw_button_with_shadow(surface, rect, color)

            # Малюємо текст на кнопці
            text_surface = self.small_font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

    def _draw_button_with_shadow(self, surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int]):
        """Малює кнопку з тінню та заокругленими краями"""
        # Тінь кнопки (зміщена на 2 пікселі)
        shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        shadow_color = (50, 50, 50, 100)  # Темно-сірий з прозорістю
        self._draw_rounded_rect(surface, shadow_color, shadow_rect, border_radius=15)

        # Основна кнопка
        self._draw_rounded_rect(surface, color, rect, border_radius=15, border_width=2, border_color=BLACK)

        # Відблиск на кнопці для об'ємного ефекту
        highlight_color = (min(255, color[0] + 30), min(255, color[1] + 30), min(255, color[2] + 30))
        highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 3)
        self._draw_rounded_rect(surface, highlight_color, highlight_rect, border_radius=12)

    def _draw_rounded_rect(self, surface: pygame.Surface, color, rect: pygame.Rect,
                           border_radius: int = 10, border_width: int = 0, border_color=BLACK):
        """Малює заокруглений прямокутник"""
        # Якщо колір має альфа-канал (4 компоненти)
        if len(color) == 4:
            # Створюємо тимчасову поверхню з альфа-каналом
            temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surface, color, (0, 0, rect.width, rect.height), border_radius=border_radius)
            surface.blit(temp_surface, rect.topleft)
        else:
            # Звичайний колір без альфа-каналу
            pygame.draw.rect(surface, color, rect, border_radius=border_radius)

        # Якщо потрібна рамка
        if border_width > 0:
            pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)