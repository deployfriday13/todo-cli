from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


class Priority(StrEnum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class Task:
    title: str
    created_at: datetime
    id: int | None = None
    completed: bool = False
    completed_at: datetime | None = None
    due_date: date | None = None
    priority: Priority = Priority.NORMAL

    def __post_init__(self):
        if isinstance(self.priority, str):
            self.priority = Priority(self.priority)
        if isinstance(self.due_date, str):
            self.due_date = date.fromisoformat(self.due_date)
