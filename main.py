"""
Головний файл для запуску гри судоку
"""
import os
import sys

from sudoku import Game

# Додавання поточної директорії до шляху для імпорту модулів
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))




def main():
    """Головна функція для запуску гри"""
    # Встановлення позиції вікна
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (400, 100)

    try:
        # Створення та запуск гри
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error when starting the game: {e}")
        input("Press Enter for closing...")


if __name__ == "__main__":
    main()