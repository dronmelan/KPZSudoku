"""
Модуль для відображення дошки судоку та інтерфейсу
"""
import pygame
from typing import List, Optional, Tuple, Dict

from ..config import (
    GRID_SIZE, SUB_GRID_SIZE, CELL_SIZE, WINDOW_SIZE,
    BLACK, WHITE, GRAY, BLUE, GREEN, LIGHT_BLUE, LIGHT_BLUE_ALT, LIGHT_GRAY
)
from ..models import Cell


class SudokuRenderer:
    """Клас для відображення судоку"""
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.cell_size = CELL_SIZE

        # Розрахунок зсувів для центрування
        self.grid_width = GRID_SIZE * self.cell_size
        self.grid_height = GRID_SIZE * self.cell_size

        # Зсув по горизонталі для центрування сітки
        self.grid_offset_x = (WINDOW_SIZE[0] - self.grid_width) // 2
        # Зсув по вертикалі з урахуванням місця для UI елементів
        self.grid_offset_y = 20  # Відступ зверху

    def draw_grid(self, surface: pygame.Surface, grid: List[List[Cell]], selected_cell: Optional[Tuple[int, int]]):
        """Малює сітку судоку"""
        # Малювання клітинок
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = grid[row][col]
                rect = pygame.Rect(
                    col * self.cell_size + self.grid_offset_x,
                    row * self.cell_size + self.grid_offset_y,
                    self.cell_size,
                    self.cell_size
                )

                # Встановлення кольору фону клітинки
                bg_color = WHITE
                if selected_cell and selected_cell[0] == row and selected_cell[1] == col:
                    bg_color = GRAY  # Світло-блакитний для виділеної клітинки
                elif selected_cell and (selected_cell[0] == row or selected_cell[1] == col):
                    bg_color = LIGHT_GRAY  # Світло-синій для виділеного рядка/колонки

                pygame.draw.rect(surface, bg_color, rect)

                # Малювання значення клітинки
                if cell.value != 0:
                    color = BLACK if cell.is_fixed or cell.is_valid else pygame.Color("red")
                    text = self.font.render(str(cell.value), True, color)
                    text_rect = text.get_rect(
                        center=(col * self.cell_size + self.cell_size // 2 + self.grid_offset_x,
                               row * self.cell_size + self.cell_size // 2 + self.grid_offset_y)
                    )
                    surface.blit(text, text_rect)
                # Малювання заміток
                elif len(cell.notes) > 0:
                    for note in cell.notes:
                        # Визначення позиції для кожної примітки (3x3 сітка всередині клітинки)
                        note_row = (note - 1) // 3
                        note_col = (note - 1) % 3
                        note_x = (col * self.cell_size + note_col * (self.cell_size // 3) +
                                 self.cell_size // 6 + self.grid_offset_x)
                        note_y = (row * self.cell_size + note_row * (self.cell_size // 3) +
                                 self.cell_size // 6 + self.grid_offset_y)

                        text = self.small_font.render(str(note), True, GRAY)
                        text_rect = text.get_rect(center=(note_x, note_y))
                        surface.blit(text, text_rect)

        # Малювання ліній сітки
        for i in range(GRID_SIZE + 1):
            line_thickness = 3 if i % SUB_GRID_SIZE == 0 else 1

            # Горизонтальні лінії
            pygame.draw.line(
                surface,
                BLACK,
                (self.grid_offset_x, i * self.cell_size + self.grid_offset_y),
                (self.grid_offset_x + GRID_SIZE * self.cell_size, i * self.cell_size + self.grid_offset_y),
                line_thickness
            )

            # Вертикальні лінії
            pygame.draw.line(
                surface,
                BLACK,
                (i * self.cell_size + self.grid_offset_x, self.grid_offset_y),
                (i * self.cell_size + self.grid_offset_x, self.grid_offset_y + GRID_SIZE * self.cell_size),
                line_thickness
            )

    def draw_blurred_grid(self, surface: pygame.Surface):
        """Малює розмиту сітку для стану паузи"""
        # Створюємо напівпрозорий overlay
        overlay = pygame.Surface((GRID_SIZE * self.cell_size, GRID_SIZE * self.cell_size))
        overlay.set_alpha(200)
        overlay.fill(GRAY)

        # Малюємо основну структуру сітки без значень
        for i in range(GRID_SIZE + 1):
            line_thickness = 3 if i % SUB_GRID_SIZE == 0 else 1

            # Горизонтальні лінії
            pygame.draw.line(
                overlay,
                BLACK,
                (0, i * self.cell_size),
                (GRID_SIZE * self.cell_size, i * self.cell_size),
                line_thickness
            )

            # Вертикальні лінії
            pygame.draw.line(
                overlay,
                BLACK,
                (i * self.cell_size, 0),
                (i * self.cell_size, GRID_SIZE * self.cell_size),
                line_thickness
            )

        surface.blit(overlay, (self.grid_offset_x, self.grid_offset_y))

    def draw_buttons(self, surface: pygame.Surface, buttons: dict) -> None:
        """Відображення кнопок з обробкою помилок"""
        try:
            if not buttons:
                return

            # Перевірка структури buttons
            valid_buttons = []
            for key, value in buttons.items():
                try:
                    if isinstance(value, (list, tuple)) and len(value) > 0:
                        button = value[0]  # Перший елемент - це кнопка
                        if hasattr(button, 'width'):
                            valid_buttons.append((button, value))
                        else:
                            print(f"Кнопка {key} не має атрибуту width")
                    else:
                        print(f"Неправильна структура кнопки {key}: {value}")
                except Exception as e:
                    print(f"Помилка обробки кнопки {key}: {e}")
                    continue

            if not valid_buttons:
                return

            # Розрахунок загальної ширини кнопок
            try:
                total_button_width = sum(button.width for button, _ in valid_buttons)
            except Exception as e:
                print(f"Помилка розрахунку ширини кнопок: {e}")
                return

            # Відображення кнопок
            for button, button_data in valid_buttons:
                try:
                    # Ваш код для відображення кнопки
                    # Наприклад:
                    button.draw(surface)
                except Exception as e:
                    print(f"Помилка відображення кнопки: {e}")

        except Exception as e:
            print(f"Загальна помилка в draw_buttons: {e}")

    def draw_hints_counter(self, surface: pygame.Surface, hints_text: str):
        """Малює лічильник підказок під кнопками"""
        hints_counter = self.small_font.render(hints_text, True, BLACK)
        hints_rect = hints_counter.get_rect()
        # Центруємо під кнопками
        hints_rect.centerx = WINDOW_SIZE[0] // 2
        hints_rect.y = self.grid_offset_y + GRID_SIZE * self.cell_size + 100
        surface.blit(hints_counter, hints_rect)

    def draw_timer(self, surface: pygame.Surface, time_str: str):
        """Малює таймер"""
        timer_text = self.font.render(f"Time: {time_str}", True, BLACK)
        timer_rect = timer_text.get_rect()
        # Центруємо таймер під сіткою з більшою відстанню
        timer_rect.centerx = WINDOW_SIZE[0] // 2
        timer_rect.y = self.grid_offset_y + GRID_SIZE * self.cell_size + 25
        surface.blit(timer_text, timer_rect)

    def draw_pause_message(self, surface: pygame.Surface):
        """Малює повідомлення про паузу"""
        # Створюємо напівпрозорий фон для повідомлення
        message_width = 350
        message_height = 120
        message_bg = pygame.Surface((message_width, message_height))
        message_bg.set_alpha(240)
        message_bg.fill(WHITE)

        # Центруємо повідомлення відносно сітки
        grid_center_x = self.grid_offset_x + (GRID_SIZE * self.cell_size) // 2
        grid_center_y = self.grid_offset_y + (GRID_SIZE * self.cell_size) // 2

        message_rect = message_bg.get_rect(center=(grid_center_x, grid_center_y))
        surface.blit(message_bg, message_rect)

        # Рамка навколо повідомлення
        pygame.draw.rect(surface, BLACK, message_rect, 3)

        # Текст повідомлення
        pause_text = self.font.render("PAUSE", True, BLACK)
        pause_rect = pause_text.get_rect(center=(grid_center_x, grid_center_y - 15))
        surface.blit(pause_text, pause_rect)

        # Інструкція
        instruction_text = self.small_font.render("Press 'Space' to continue", True, BLACK)
        instruction_rect = instruction_text.get_rect(center=(grid_center_x, grid_center_y + 15))
        surface.blit(instruction_text, instruction_rect)

    def draw_game_over(self, surface: pygame.Surface):
        """Малює повідомлення про завершення гри"""
        # Напівпрозорий overlay тільки для ігрової області
        overlay = pygame.Surface((GRID_SIZE * self.cell_size, GRID_SIZE * self.cell_size))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        surface.blit(overlay, (self.grid_offset_x, self.grid_offset_y))

        # Центруємо повідомлення відносно сітки
        grid_center_x = self.grid_offset_x + (GRID_SIZE * self.cell_size) // 2
        grid_center_y = self.grid_offset_y + (GRID_SIZE * self.cell_size) // 2

        text = self.font.render("Congratulations!", True, GREEN)
        text_rect = text.get_rect(center=(grid_center_x, grid_center_y))
        surface.blit(text, text_rect)

        subtext = self.small_font.render("Press 'N', to restart game", True, WHITE)
        subtext_rect = subtext.get_rect(center=(grid_center_x, grid_center_y + 40))
        surface.blit(subtext, subtext_rect)

    def get_cell_from_pos(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Повертає координати клітинки за позицією миші з урахуванням зсувів"""
        x, y = pos

        # Перевіряємо, чи знаходиться позиція в межах сітки
        if (self.grid_offset_x <= x < self.grid_offset_x + self.grid_width and
            self.grid_offset_y <= y < self.grid_offset_y + self.grid_height):

            col = (x - self.grid_offset_x) // self.cell_size
            row = (y - self.grid_offset_y) // self.cell_size

            return (row, col)

        return None