"""
Модуль для генерації судоку
"""
from abc import ABC, abstractmethod
import random
from copy import deepcopy
from typing import List, Tuple

from ..config import GRID_SIZE, SUB_GRID_SIZE
from ..models import Difficulty


class ISudokuGenerator(ABC):
    """Інтерфейс для генератора судоку"""
    @abstractmethod
    def generate(self, difficulty: Difficulty) -> Tuple[List[List[int]], List[List[int]]]:
        """Генерує нову сітку судоку заданої складності"""
        pass


class SudokuGenerator(ISudokuGenerator):
    """Клас для генерації судоку"""
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def _is_valid(self, row: int, col: int, num: int) -> bool:
        """Перевіряє, чи можна поставити число num в задану позицію"""
        # Перевірка рядка і колонки
        for i in range(GRID_SIZE):
            if self.grid[row][i] == num or self.grid[i][col] == num:
                return False

        # Перевірка блоку 3x3
        start_row = row - row % SUB_GRID_SIZE
        start_col = col - col % SUB_GRID_SIZE
        for i in range(SUB_GRID_SIZE):
            for j in range(SUB_GRID_SIZE):
                if self.grid[start_row + i][start_col + j] == num:
                    return False
        return True

    def _solve(self) -> bool:
        """Заповнює сітку судоку з використанням алгоритму backtracking"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 0:
                    nums = list(range(1, GRID_SIZE + 1))
                    random.shuffle(nums)
                    for num in nums:
                        if self._is_valid(row, col, num):
                            self.grid[row][col] = num
                            if self._solve():
                                return True
                            self.grid[row][col] = 0
                    return False
        return True

    def generate(self, difficulty: Difficulty) -> Tuple[List[List[int]], List[List[int]]]:
        """Генерує нове судоку заданої складності"""
        # Очищення сітки
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Створення повного розв'язку
        self._solve()

        # Копіювання розв'язку
        solution = deepcopy(self.grid)

        # Видалення клітинок відповідно до рівня складності
        cells = [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)]
        random.shuffle(cells)

        cells_to_keep = difficulty.value
        cells_to_remove = GRID_SIZE * GRID_SIZE - cells_to_keep

        for i in range(cells_to_remove):
            row, col = cells[i]
            self.grid[row][col] = 0

        return self.grid, solution