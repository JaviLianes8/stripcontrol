"""Remove or detect control characters and terminal escape sequences in text."""

from __future__ import annotations

from ._bytes import strip_control_bytes
from ._control import STANDARD_WHITESPACE, escape_control, find_control, has_control
from ._format_table import UNICODE_VERSION
from ._stripper import ControlStripper, strip_control

__version__ = "0.2.0"

__all__ = [
    "STANDARD_WHITESPACE",
    "UNICODE_VERSION",
    "ControlStripper",
    "escape_control",
    "find_control",
    "has_control",
    "strip_control",
    "strip_control_bytes",
]
