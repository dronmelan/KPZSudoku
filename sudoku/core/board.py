"""
Модуль для представлення дошки судоку
"""
from abc import ABC, abstractmethod
import random
from typing import List, Optional, Tuple

from ..config import GRID_SIZE, MAX_HINTS
from ..models import Cell, Difficulty
from .generator import ISudokuGenerator
from .validator import SudokuValidator


class ISudokuBoard(ABC):
    """Інтерфейс для дошки судоку"""
    @abstractmethod
    def initialize(self, difficulty: Difficulty) -> None:
        """Ініціалізує нову дошку судоку"""
        pass

    @abstractmethod
    def set_value(self, row: int, col: int, value: int) -> bool:
        """Встановлює значення у вказаній клітинці"""
        pass

    @abstractmethod
    def is_complete(self) -> bool:
        """Перевіряє, чи завершена гра"""
        pass

    @abstractmethod
    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """Повертає підказку для поточної позиції"""
        pass


class SudokuBoard(ISudokuBoard):
    """Клас для представлення дошки судоку"""
    def __init__(self, generator: ISudokuGenerator):
        self.generator = generator
        self.grid: List[List[Cell]] = [[Cell(row, col) for col in range(GRID_SIZE)] for row in range(GRID_SIZE)]
        self.solution = None
        self.validator = SudokuValidator()
        self.hints_used = 0
        self.max_hints = MAX_HINTS

    def initialize(self, difficulty: Difficulty) -> None:
        """Ініціалізує нову дошку судоку"""
        puzzle, self.solution = self.generator.generate(difficulty)

        self.grid = [[Cell(row, col) for col in range(GRID_SIZE)] for row in range(GRID_SIZE)]
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = puzzle[row][col]
                cell = self.grid[row][col]
                cell.value = value
                cell.is_fixed = (value != 0)

        self.hints_used = 0

    def set_value(self, row: int, col: int, value: int) -> bool:
        """Встановлює значення у вказаній клітинці і перевіряє його правильність"""
        cell = self.grid[row][col]

        if cell.is_fixed:
            return False

        is_valid = self.validator.is_valid_move(self.grid, row, col, value)

        if cell.set_value(value):
            cell.is_valid = is_valid
            return True
        return False

    def toggle_note(self, row: int, col: int, value: int) -> None:
        """Додає або видаляє замітку"""
        self.grid[row][col].toggle_note(value)

    def clear_cell(self, row: int, col: int) -> bool:
        """Очищає вибрану клітинку"""
        return self.set_value(row, col, 0)

    def is_complete(self) -> bool:
        """Перевіряє, чи завершена гра"""
        return (self.validator.is_board_complete(self.grid) and
                self.validator.is_board_valid(self.grid))

    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """Повертає підказку для однієї клітинки"""
        if self.hints_used >= self.max_hints:
            return None

        # Пошук незаповненої клітинки
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col].value == 0:
                    empty_cells.append((row, col))

        if not empty_cells:
            return None

        # Вибір випадкової клітинки і надання підказки
        row, col = random.choice(empty_cells)
        correct_value = self.solution[row][col]

        self.hints_used += 1
        return row, col, correct_value

    def auto_notes(self) -> None:
        """Автоматично заповнює примітки для всіх клітинок"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = self.grid[row][col]
                if cell.value == 0 and not cell.is_fixed:
                    cell.notes.clear()
                    for num in range(1, GRID_SIZE + 1):
                        if self.validator.is_valid_move(self.grid, row, col, num):
                            cell.notes.add(num)