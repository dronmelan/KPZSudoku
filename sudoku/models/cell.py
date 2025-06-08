"""
Модуль для клітинки судоку
"""
from typing import Set


class Cell:
    """Клас для представлення окремої клітинки Судоку"""
    def __init__(self, row: int, col: int, value: int = 0, is_fixed: bool = False):
        self.row = row
        self.col = col
        self.value = value
        self.is_fixed = is_fixed  # Фіксовані клітинки не можна змінювати
        self.notes: Set[int] = set()  # Замітки гравця
        self.is_selected = False
        self.is_valid = True  # Для відображення невірно введених цифр

    def set_value(self, value: int) -> bool:
        """Встановлює значення клітинки, якщо вона не фіксована"""
        if not self.is_fixed:
            self.value = value
            self.notes.clear()  # Очищення заміток при встановленні значення
            return True
        return False

    def toggle_note(self, value: int) -> None:
        """Додає або видаляє примітку"""
        if not self.is_fixed and self.value == 0:
            if value in self.notes:
                self.notes.remove(value)
            else:
                self.notes.add(value)