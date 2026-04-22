import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from todo.task import Task

sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
sqlite3.register_converter("TIMESTAMP", lambda b: datetime.fromisoformat(b.decode()))


class TaskRepository:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        sql_path = Path(__file__).parent / "schema.sql"
        with open(sql_path) as f:
            stmt = f.read()
        with self._connect() as conn:
            conn.executescript(stmt)

    def get_pending(self) -> list[Task]:
        query = "SELECT * FROM tasks WHERE completed=0"
        with self._connect() as conn:
            raw = conn.execute(query)

        return [Task(**task) for task in raw]

    def get_all(self) -> list[Task]:
        query = "SELECT * FROM tasks"
        with self._connect() as conn:
            raw = conn.execute(query)

        return [Task(**task) for task in raw]

    def add(self, title: str) -> Task:
        stmt = "INSERT INTO tasks (title, created_at) VALUES (?, ?)"
        now = datetime.now(timezone.utc)

        with self._connect() as conn:
            cursor = conn.execute(stmt, (title, now))
        return Task(id=cursor.lastrowid, title=title, created_at=datetime.now())

    def mark_done(self, task_id: int) -> None:
        stmt = "UPDATE tasks SET completed=?, completed_at=? WHERE id = (?)"
        now = datetime.now(timezone.utc)

        with self._connect() as conn:
            conn.execute(stmt, (True, now, task_id))

    def mark_undo(self, task_id: int) -> None:
        stmt = "UPDATE tasks SET completed=?, completed_at=? WHERE id = (?)"

        with self._connect() as conn:
            conn.execute(stmt, (False, None, task_id))

    def delete(self, task_id: int) -> None:
        stmt = "DELETE FROM tasks WHERE id=?"
        with self._connect() as conn:
            conn.execute(stmt, (task_id,))

    def delete_completed(self) -> None:
        stmt = "DELETE FROM tasks WHERE completed=1"
        with self._connect() as conn:
            conn.execute(stmt)

    def search(self, query: str) -> list[Task]:
        stmt = "SELECT * FROM tasks WHERE title LIKE ?"
        with self._connect() as conn:
            raw = conn.execute(stmt, (f"%{query}%",))

        return [Task(**task) for task in raw]


tr = TaskRepository("./todo.db")
tr.add("Купить корм мурзику")
task = tr.search("корм")

print(task)
