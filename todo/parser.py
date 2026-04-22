import sys
from dataclasses import dataclass, field
from datetime import date

USAGE = """\
usage: todo <command> [args]

commands:
  add <title> [--due YYYY-MM-DD] [--priority high|normal|low]
                     Add a new task
  list [--all] [--limit N]
                     List tasks (--all includes completed)
  done [<id>]        Mark a task as completed (interactive if no ID)
  undo <id>          Mark a task as not completed
  edit <id> <title>  Rename a task
  delete <id>        Delete a task
  clear              Delete all completed tasks
  search <query>     Search tasks by title"""


@dataclass
class AddArgs:
    title: str
    due_date: date | None = None
    priority: str = "normal"


@dataclass
class ListArgs:
    show_all: bool = False
    limit: int | None = None


@dataclass
class DoneArgs:
    id: int | None = None


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


@dataclass
class EditArgs:
    id: int
    title: str


Args = AddArgs | ListArgs | DoneArgs | UndoArgs | DeleteArgs | ClearArgs | SearchArgs | EditArgs


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
            due_date = None
            priority = "normal"
            title_tokens = []
            i = 0
            while i < len(rest):
                match rest[i]:
                    case "--due":
                        if i + 1 >= len(rest):
                            raise SystemExit("todo add: --due requires a value")
                        try:
                            due_date = date.fromisoformat(rest[i + 1])
                        except ValueError:
                            raise SystemExit("todo add: --due must be YYYY-MM-DD")
                        i += 2
                    case "--priority":
                        if i + 1 >= len(rest):
                            raise SystemExit("todo add: --priority requires a value")
                        if rest[i + 1] not in ("high", "normal", "low"):
                            raise SystemExit("todo add: --priority must be high, normal, or low")
                        priority = rest[i + 1]
                        i += 2
                    case token:
                        title_tokens.append(token)
                        i += 1
            if not title_tokens:
                raise SystemExit("usage: todo add <title> [--due YYYY-MM-DD] [--priority high|normal|low]")
            return AddArgs(title=" ".join(title_tokens), due_date=due_date, priority=priority)

        case "list":
            show_all = False
            limit = None
            i = 0
            while i < len(rest):
                match rest[i]:
                    case "--all":
                        show_all = True
                        i += 1
                    case "--limit":
                        if i + 1 >= len(rest):
                            raise SystemExit("todo list: --limit requires a value")
                        try:
                            limit = int(rest[i + 1])
                        except ValueError:
                            raise SystemExit("todo list: --limit must be an integer")
                        i += 2
                    case unknown:
                        raise SystemExit(f"todo list: unknown option '{unknown}'")
            return ListArgs(show_all=show_all, limit=limit)

        case "done":
            if len(rest) == 0:
                return DoneArgs(id=None)
            if len(rest) != 1:
                raise SystemExit("usage: todo done [<id>]")
            return DoneArgs(id=_parse_id(rest[0], "done"))

        case "undo":
            if len(rest) != 1:
                raise SystemExit("usage: todo undo <id>")
            return UndoArgs(id=_parse_id(rest[0], "undo"))

        case "edit":
            if len(rest) < 2:
                raise SystemExit("usage: todo edit <id> <title>")
            return EditArgs(id=_parse_id(rest[0], "edit"), title=" ".join(rest[1:]))

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
