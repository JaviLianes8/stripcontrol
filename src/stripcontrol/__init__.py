"""Remove or detect C0/C1 control characters from text while keeping standard whitespace."""

from __future__ import annotations

from ._control import STANDARD_WHITESPACE, find_control, has_control, strip_control

__version__ = "0.1.0"

__all__ = [
    "STANDARD_WHITESPACE",
    "find_control",
    "has_control",
    "strip_control",
]
