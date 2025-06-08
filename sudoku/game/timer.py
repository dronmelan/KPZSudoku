"""
Модуль для таймеру гри
"""
import pygame


class GameTimer:
    """Клас для відстеження часу гри"""
    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0
        self.is_running = False

    def start(self):
        """Запускає таймер"""
        self.start_time = pygame.time.get_ticks()
        self.is_running = True

    def pause(self):
        """Ставить таймер на паузу"""
        if self.is_running:
            self.elapsed_time += pygame.time.get_ticks() - self.start_time
            self.is_running = False

    def resume(self):
        """Відновлює таймер після паузи"""
        if not self.is_running:
            self.start_time = pygame.time.get_ticks()
            self.is_running = True

    def reset(self):
        """Скидає таймер"""
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.is_running = True

    def update(self):
        """Оновлює таймер (викликається кожен кадр)"""
        # Метод для сумісності, фактично час обчислюється в get_time()
        pass

    def get_time(self) -> int:
        """Повертає поточний час в мілісекундах"""
        if self.is_running:
            return self.elapsed_time + pygame.time.get_ticks() - self.start_time
        return self.elapsed_time

    def get_formatted_time(self) -> str:
        """Повертає відформатований час у вигляді MM:SS"""
        total_seconds = self.get_time() // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"