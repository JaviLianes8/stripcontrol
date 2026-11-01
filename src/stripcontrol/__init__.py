r"""Remove or detect control characters and terminal escape sequences in text.

The public constants describe the default kept controls and the pinned Unicode data.

>>> from stripcontrol import STANDARD_WHITESPACE, UNICODE_VERSION
>>> STANDARD_WHITESPACE
'\t\n\r'
>>> UNICODE_VERSION
'18.0.0'
"""

from __future__ import annotations

from ._bytes import strip_control_bytes
from ._control import STANDARD_WHITESPACE, escape_control, find_control, has_control
from ._format_table import UNICODE_VERSION
from ._stripper import ControlStripper, strip_control

del annotations

__version__ = "1.0.0"

ControlStripper.__module__ = "stripcontrol"

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
