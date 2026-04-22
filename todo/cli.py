import sys
from datetime import date
from pathlib import Path

from todo.db.repository import SQLiteTaskRepository
from todo.exceptions import TaskNotFound
from todo.parser import (
    AddArgs,
    ClearArgs,
    DeleteArgs,
    DoneArgs,
    EditArgs,
    ListArgs,
    SearchArgs,
    UndoArgs,
    parse_args,
)
from todo.style import Style, styled
from todo.task import Priority, Task

DB_PATH = Path.home() / ".todo.db"

_PRIORITY_ORDER = {Priority.HIGH: 0, Priority.NORMAL: 1, Priority.LOW: 2}


def _sort_key(task: Task) -> tuple:
    return (_PRIORITY_ORDER[task.priority], task.due_date or date.max, task.id)


def _format(task: Task) -> str:
    today = date.today()

    meta = []
    if task.priority != Priority.NORMAL:
        meta.append(task.priority)
    if task.due_date:
        meta.append(task.due_date.isoformat())

    meta_str = "  " + "  ".join(meta) if meta else ""
    line = f"{task.id:>3} | {task.title}{meta_str}"

    if task.completed:
        return styled(line, Style.DIM, Style.STRIKETHROUGH)
    if task.due_date and task.due_date < today:
        return styled(line, Style.RED)
    if task.priority == Priority.HIGH:
        return styled(line, Style.YELLOW)
    if task.priority == Priority.LOW:
        return styled(line, Style.DIM)
    return line


def _print_tasks(tasks: list[Task], limit: int | None = None) -> None:
    if not tasks:
        print("No tasks")
        return
    pending = sorted([t for t in tasks if not t.completed], key=_sort_key)
    done = [t for t in tasks if t.completed]
    ordered = pending + done
    if limit is not None:
        ordered = ordered[:limit]
    for task in ordered:
        print(_format(task))


def main() -> None:
    args = parse_args()
    repo = SQLiteTaskRepository(str(DB_PATH))

    try:
        match args:
            case AddArgs(title=title, due_date=due_date, priority=priority):
                task = repo.add(title, due_date=due_date, priority=priority)
                print(f"Added [{task.id}]: {task.title}")

            case ListArgs(show_all=show_all, limit=limit):
                tasks = repo.get_all() if show_all else repo.get_pending()
                _print_tasks(tasks, limit=limit)

            case DoneArgs(id=None):
                tasks = repo.get_pending()
                if not tasks:
                    print("No pending tasks")
                    return
                _print_tasks(tasks)
                try:
                    task_id = int(input("\nTask ID: "))
                except (ValueError, EOFError):
                    raise SystemExit("Error: invalid ID")
                repo.mark_done(task_id)
                print(f"Task {task_id} marked as done")

            case DoneArgs(id=task_id):
                repo.mark_done(task_id)
                print(f"Task {task_id} marked as done")

            case UndoArgs(id=task_id):
                repo.mark_undo(task_id)
                print(f"Task {task_id} marked as not done")

            case EditArgs(id=task_id, title=title):
                repo.edit(task_id, title)
                print(f"Task {task_id} updated")

            case DeleteArgs(id=task_id):
                repo.delete(task_id)
                print(f"Task {task_id} deleted")

            case ClearArgs():
                repo.delete_completed()
                print("Completed tasks cleared")

            case SearchArgs(query=query):
                tasks = repo.search(query)
                _print_tasks(tasks)

    except TaskNotFound as e:
        print(f"Error: task {e} not found", file=sys.stderr)
        sys.exit(1)
