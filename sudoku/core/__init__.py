"""
Пакет для основних компонентів гри
"""
from .generator import ISudokuGenerator, SudokuGenerator
from .validator import SudokuValidator
from .board import ISudokuBoard, SudokuBoard

__all__ = [
    'ISudokuGenerator', 'SudokuGenerator',
    'SudokuValidator',
    'ISudokuBoard', 'SudokuBoard'
]