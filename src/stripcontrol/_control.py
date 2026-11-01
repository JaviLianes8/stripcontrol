"""Classify control and format characters; detect, list and escape them one by one."""

from __future__ import annotations

import re

from ._format_table import FORMAT_RANGES

STANDARD_WHITESPACE = "\t\n\r"
"""Control characters that are ordinary text whitespace and are kept by default."""

# Unicode Cc is exactly C0, DEL and C1: U+0000..U+001F and U+007F..U+009F.
_CONTROL_CLASS = "\x00-\x1f\x7f-\x9f"


def _class_item(code: int) -> str:
    return f"\\U{code:08x}"


_FORMAT_CLASS = "".join(
    _class_item(start) if start == end else f"{_class_item(start)}-{_class_item(end)}"
    for start, end in FORMAT_RANGES
)
CONTROLS = re.compile(f"[{_CONTROL_CLASS}]")
CONTROLS_AND_FORMAT = re.compile(f"[{_CONTROL_CLASS}{_FORMAT_CLASS}]")


def pattern(format_chars: bool) -> re.Pattern[str]:
    """The character class to act on: controls, plus format characters when asked."""
    check_bool(format_chars, "format_chars")
    return CONTROLS_AND_FORMAT if format_chars else CONTROLS


def check_text(text: object, name: str = "text") -> str:
    if not issubclass(type(text), str):
        raise TypeError(f"{name} must be str")
    return str.__str__(text)


def check_bool(value: bool, name: str) -> None:
    if type(value) is not bool:
        raise TypeError(f"{name} must be bool")


def has_control(text: str, *, keep: str = STANDARD_WHITESPACE, format_chars: bool = False) -> bool:
    r"""Report whether ``text`` holds a control character that is not in ``keep``.

    With ``format_chars=True`` Unicode format characters (category Cf) count as well.
    Wrong argument types raise TypeError without quoting input.

    >>> from stripcontrol import has_control
    >>> has_control("ok\n"), has_control("x\x00")
    (False, True)
    """
    text = check_text(text)
    kept = frozenset(check_text(keep, "keep"))
    return any(match.group() not in kept for match in pattern(format_chars).finditer(text))


def find_control(
    text: str, *, keep: str = STANDARD_WHITESPACE, format_chars: bool = False
) -> list[tuple[int, int]]:
    r"""List ``(index, codepoint)`` for each control character in ``text`` not in ``keep``.

    With ``format_chars=True`` Unicode format characters (category Cf) are listed too.
    Indexes count Unicode code points, starting at zero. Wrong types raise TypeError.

    >>> from stripcontrol import find_control
    >>> find_control("a\x00b\n")
    [(1, 0)]
    """
    text = check_text(text)
    kept = frozenset(check_text(keep, "keep"))
    return [
        (match.start(), ord(match.group()))
        for match in pattern(format_chars).finditer(text)
        if match.group() not in kept
    ]


def escape_control(
    text: str, *, keep: str = STANDARD_WHITESPACE, format_chars: bool = False
) -> str:
    r"""Return ``text`` with each control character not in ``keep`` written as an escape.

    A character below U+0100 becomes ``\xNN``, others ``\uNNNN`` or ``\UNNNNNNNN``, so
    a log keeps the evidence of an escape sequence without the terminal acting on it. The
    result is meant for display: backslashes already in ``text`` are left as they are.
    Wrong argument types raise TypeError.

    >>> from stripcontrol import escape_control
    >>> print(escape_control("a\x1b[31m"))
    a\x1b[31m
    """
    text = check_text(text)
    kept = frozenset(check_text(keep, "keep"))

    def replace(match: re.Match[str]) -> str:
        char = match.group()
        return char if char in kept else escape_char(ord(char))

    return pattern(format_chars).sub(replace, text)


def escape_char(code: int) -> str:
    if code < 0x100:
        return f"\\x{code:02x}"
    if code < 0x10000:
        return f"\\u{code:04x}"
    return f"\\U{code:08x}"
