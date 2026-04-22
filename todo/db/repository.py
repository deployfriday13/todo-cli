import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path

from todo.exceptions import TaskNotFound
from todo.task import Task


class TaskRepository(ABC):
    @abstractmethod
    def get_pending(self) -> list[Task]: ...

    @abstractmethod
    def get_all(self) -> list[Task]: ...

    @abstractmethod
    def add(self, title: str) -> Task: ...

    @abstractmethod
    def mark_done(self, task_id: int) -> None: ...

    @abstractmethod
    def mark_undo(self, task_id: int) -> None: ...

    @abstractmethod
    def delete(self, task_id: int) -> None: ...

    @abstractmethod
    def delete_completed(self) -> None: ...

    @abstractmethod
    def search(self, query: str) -> list[Task]: ...


class SQLiteTaskRepository(TaskRepository):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._register_adapters()
        self._init_db()

    @staticmethod
    def _register_adapters() -> None:
        sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
        sqlite3.register_converter("TIMESTAMP", lambda b: datetime.fromisoformat(b.decode()))

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        sql = (Path(__file__).parent / "schema.sql").read_text()
        with self._connect() as conn:
            conn.executescript(sql)

    def get_pending(self) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tasks WHERE completed=0").fetchall()
        return [Task(**row) for row in rows]

    def get_all(self) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM tasks").fetchall()
        return [Task(**row) for row in rows]

    def add(self, title: str) -> Task:
        now = datetime.now(timezone.utc)
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, created_at) VALUES (?, ?)", (title, now)
            )
        return Task(id=cursor.lastrowid, title=title, created_at=now)

    def mark_done(self, task_id: int) -> None:
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE tasks SET completed=1, completed_at=? WHERE id=?",
                (datetime.now(timezone.utc), task_id),
            )
            if cursor.rowcount == 0:
                raise TaskNotFound(task_id)

    def mark_undo(self, task_id: int) -> None:
        with self._connect() as conn:
            cursor = conn.execute(
                "UPDATE tasks SET completed=0, completed_at=NULL WHERE id=?",
                (task_id,),
            )
            if cursor.rowcount == 0:
                raise TaskNotFound(task_id)

    def delete(self, task_id: int) -> None:
        with self._connect() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            if cursor.rowcount == 0:
                raise TaskNotFound(task_id)

    def delete_completed(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE completed=1")

    def search(self, query: str) -> list[Task]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE title LIKE ?", (f"%{query}%",)
            ).fetchall()
        return [Task(**row) for row in rows]
