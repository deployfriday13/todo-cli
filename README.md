# todo-cli

A minimal command-line task manager written in Python. Tasks are stored in a local SQLite database at `~/.todo.db`.

## Installation

```bash
git clone git@github.com:deployfriday13/todo-cli.git
cd todo-cli
pip install -e .
```

Requires Python 3.14+.

## Usage

Running `todo` with no arguments lists all pending tasks.

```bash
todo
```

### Commands

| Command | Description |
|---|---|
| `todo add <title>` | Add a new task |
| `todo list` | List pending tasks |
| `todo list --all` | List all tasks including completed |
| `todo list --limit <n>` | Limit the number of tasks shown |
| `todo done [<id>]` | Mark a task as completed (interactive prompt if no ID given) |
| `todo undo <id>` | Mark a task as not completed |
| `todo edit <id> <title>` | Rename a task |
| `todo delete <id>` | Delete a task |
| `todo clear` | Delete all completed tasks |
| `todo search <query>` | Search tasks by title |

### Options for `add`

| Option | Description |
|---|---|
| `--due YYYY-MM-DD` | Set a due date |
| `--priority high\|normal\|low` | Set priority (default: `normal`) |

### Examples

```bash
todo add Buy milk
todo add Submit report --due 2026-04-30 --priority high
todo list --all --limit 10
todo done
todo edit 3 Submit final report
todo search report
```

### Output format

Pending tasks are listed first, sorted by priority then due date. Completed tasks appear at the end.

- **Yellow** — high priority
- **Dim** — low priority
- **Red** — overdue
- **Dim + strikethrough** — completed
