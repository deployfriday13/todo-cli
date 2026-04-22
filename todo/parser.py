import sys
from dataclasses import dataclass

USAGE = """\
usage: todo <command> [args]

commands:
  add <title>      Add a new task
  list [--all]     List tasks (--all includes completed)
  done <id>        Mark a task as completed
  undo <id>        Mark a task as not completed
  delete <id>      Delete a task
  clear            Delete all completed tasks
  search <query>   Search tasks by title"""


@dataclass
class AddArgs:
    title: str


@dataclass
class ListArgs:
    show_all: bool


@dataclass
class DoneArgs:
    id: int


@dataclass
class UndoArgs:
    id: int


@dataclass
class DeleteArgs:
    id: int


@dataclass
class ClearArgs:
    pass


@dataclass
class SearchArgs:
    query: str


Args = AddArgs | ListArgs | DoneArgs | UndoArgs | DeleteArgs | ClearArgs | SearchArgs


def _parse_id(value: str, command: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"todo {command}: <id> must be an integer")


def parse_args(argv: list[str] | None = None) -> Args:
    tokens = sys.argv[1:] if argv is None else argv

    if not tokens:
        return ListArgs(show_all=False)

    command, *rest = tokens

    match command:
        case "add":
            if not rest:
                raise SystemExit("usage: todo add <title>")
            return AddArgs(title=" ".join(rest))

        case "list":
            unknown = [t for t in rest if t != "--all"]
            if unknown:
                raise SystemExit(f"todo list: unknown option '{unknown[0]}'")
            return ListArgs(show_all="--all" in rest)

        case "done":
            if len(rest) != 1:
                raise SystemExit("usage: todo done <id>")
            return DoneArgs(id=_parse_id(rest[0], "done"))

        case "undo":
            if len(rest) != 1:
                raise SystemExit("usage: todo undo <id>")
            return UndoArgs(id=_parse_id(rest[0], "undo"))

        case "delete":
            if len(rest) != 1:
                raise SystemExit("usage: todo delete <id>")
            return DeleteArgs(id=_parse_id(rest[0], "delete"))

        case "clear":
            if rest:
                raise SystemExit("usage: todo clear")
            return ClearArgs()

        case "search":
            if not rest:
                raise SystemExit("usage: todo search <query>")
            return SearchArgs(query=" ".join(rest))

        case _:
            raise SystemExit(f"todo: unknown command '{command}'\n\n{USAGE}")
