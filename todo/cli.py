import sys
from pathlib import Path

from todo.db.repository import SQLiteTaskRepository
from todo.exceptions import TaskNotFound
from todo.parser import (
    AddArgs,
    ClearArgs,
    DeleteArgs,
    DoneArgs,
    ListArgs,
    SearchArgs,
    UndoArgs,
    parse_args,
)
from todo.style import Style, styled
from todo.task import Task

DB_PATH = Path.home() / ".todo.db"


def _format(task: Task) -> str:
    line = f"{task.id:>3} | {task.title}"
    if task.completed:
        return styled(line, Style.DIM, Style.STRIKETHROUGH)
    return line


def _print_tasks(tasks: list[Task]) -> None:
    if not tasks:
        print("No tasks")
        return
    pending = [t for t in tasks if not t.completed]
    done = [t for t in tasks if t.completed]
    for task in pending + done:
        print(_format(task))


def main() -> None:
    args = parse_args()
    repo = SQLiteTaskRepository(str(DB_PATH))

    try:
        match args:
            case AddArgs(title=title):
                task = repo.add(title)
                print(f"Added [{task.id}]: {task.title}")

            case ListArgs(show_all=show_all):
                tasks = repo.get_all() if show_all else repo.get_pending()
                _print_tasks(tasks)

            case DoneArgs(id=task_id):
                repo.mark_done(task_id)
                print(f"Task {task_id} marked as done")

            case UndoArgs(id=task_id):
                repo.mark_undo(task_id)
                print(f"Task {task_id} marked as not done")

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
