import sys
from enum import StrEnum


class Style(StrEnum):
    RESET         = "\033[0m"
    BOLD          = "\033[1m"
    DIM           = "\033[2m"
    STRIKETHROUGH = "\033[9m"
    RED           = "\033[31m"
    GREEN         = "\033[32m"
    YELLOW        = "\033[33m"
    GRAY          = "\033[90m"


def styled(text: str, *styles: Style) -> str:
    if not sys.stdout.isatty():
        return text
    return "".join(styles) + text + Style.RESET
