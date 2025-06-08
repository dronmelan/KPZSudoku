"""
Конфігураційні константи для гри Судоку
"""

# Розміри сітки
GRID_SIZE = 9
SUB_GRID_SIZE = 3
CELL_SIZE = 70

# Розміри вікна
WINDOW_WIDTH = GRID_SIZE * CELL_SIZE + 50
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE + 180
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)

# Кольори
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
BLUE = (70, 130, 180)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
LIGHT_BLUE = (173, 216, 230)
LIGHT_BLUE_ALT = (230, 240, 250)

# Налаштування підказок
MAX_HINTS = 5