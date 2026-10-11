"""Detect and remove C0/C1 control characters while keeping standard whitespace."""

from __future__ import annotations

STANDARD_WHITESPACE = "\t\n\r"
"""Control characters that are ordinary text whitespace and are kept by default."""


def _is_control(char: str) -> bool:
    code = ord(char)
    return code <= 0x1F or code == 0x7F or 0x80 <= code <= 0x9F


def strip_control(text: str, *, keep: str = STANDARD_WHITESPACE) -> str:
    """Return ``text`` with control characters removed, preserving those in ``keep``.

    Targets the C0 range (U+0000..U+001F), DEL (U+007F) and the C1 range
    (U+0080..U+009F). Characters listed in ``keep`` are left untouched, which by
    default is tab, newline and carriage return.
    """
    kept = set(keep)
    return "".join(char for char in text if char in kept or not _is_control(char))


def has_control(text: str) -> bool:
    """Report whether ``text`` holds a control character other than tab, newline or return."""
    return any(_is_control(char) and char not in STANDARD_WHITESPACE for char in text)


def find_control(text: str) -> list[tuple[int, int]]:
    """List ``(index, codepoint)`` for each control character other than standard whitespace."""
    return [
        (index, ord(char))
        for index, char in enumerate(text)
        if _is_control(char) and char not in STANDARD_WHITESPACE
    ]
