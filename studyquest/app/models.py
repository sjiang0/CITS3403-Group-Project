from dataclasses import dataclass
from typing import Optional


@dataclass
class Quest:
    id: int
    title: str
    description: str
    quest_type: str
    difficulty: str
    due_date: Optional[str] = None
    status: str = "In Progress"