"""
Моделі даних для бази даних
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

from ..models import Difficulty


@dataclass
class GameRecord:
    """Модель для запису завершеної гри"""
    id: Optional[int]
    difficulty: Difficulty
    completion_time: int  # в секундах
    hints_used: int
    score: int
    date_completed: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Конвертує об'єкт у словник"""
        return {
            'id': self.id,
            'difficulty': self.difficulty.name,
            'completion_time': self.completion_time,
            'hints_used': self.hints_used,
            'score': self.score,
            'date_completed': self.date_completed.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameRecord':
        """Створює об'єкт з словника"""
        return cls(
            id=data.get('id'),
            difficulty=Difficulty[data['difficulty']],
            completion_time=data['completion_time'],
            hints_used=data['hints_used'],
            score=data['score'],
            date_completed=datetime.fromisoformat(data['date_completed'])
        )


@dataclass
class SavedGame:
    """Модель для збереженої гри"""
    id: Optional[int]
    difficulty: Difficulty
    current_state: List[List[Dict[str, Any]]]  # Стан дошки в JSON форматі
    solution: List[List[int]]  # Розв'язок
    elapsed_time: int  # Пройдений час в секундах
    hints_used: int
    date_saved: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Конвертує об'єкт у словник"""
        return {
            'id': self.id,
            'difficulty': self.difficulty.name,
            'current_state': json.dumps(self.current_state),
            'solution': json.dumps(self.solution),
            'elapsed_time': self.elapsed_time,
            'hints_used': self.hints_used,
            'date_saved': self.date_saved.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SavedGame':
        """Створює об'єкт з словника"""
        return cls(
            id=data.get('id'),
            difficulty=Difficulty[data['difficulty']],
            current_state=json.loads(data['current_state']) if isinstance(data['current_state'], str) else data['current_state'],
            solution=json.loads(data['solution']) if isinstance(data['solution'], str) else data['solution'],
            elapsed_time=data['elapsed_time'],
            hints_used=data['hints_used'],
            date_saved=datetime.fromisoformat(data['date_saved'])
        )


@dataclass
class UserSetting:
    """Модель для налаштувань користувача"""
    id: Optional[int]
    setting_name: str
    setting_value: str

    def to_dict(self) -> Dict[str, Any]:
        """Конвертує об'єкт у словник"""
        return {
            'id': self.id,
            'setting_name': self.setting_name,
            'setting_value': self.setting_value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserSetting':
        """Створює об'єкт з словника"""
        return cls(
            id=data.get('id'),
            setting_name=data['setting_name'],
            setting_value=data['setting_value']
        )
