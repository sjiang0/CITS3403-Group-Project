from dataclasses import dataclass
from typing import Optional
from datetime import date


@dataclass
class Quest:
    id: int
    title: str
    description: str
    quest_type: str
    difficulty: str
    due_date: Optional[date] = None
    status: str = "In Progress"
    date_completed: Optional[date] = None 
