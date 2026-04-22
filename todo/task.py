from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    title: str
    created_at: datetime
    id: int | None = None
    completed: bool = False
    completed_at: datetime | None = None
