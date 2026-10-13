"""Strip bytes: C1 as two UTF-8 bytes (C2 80..C2 9F) or as one 8-bit byte (80..9F)."""

from __future__ import annotations

import re
from typing import Literal

from ._control import STANDARD_WHITESPACE, check_text
from ._stripper import strip_control

Encoding = Literal["utf-8", "latin-1"]

# Undecodable bytes travel as lone surrogates U+DC80..U+DCFF (PEP 383). Those standing for
# a stray byte 80..9F are what an 8-bit terminal would run as a C1 control.
STRAY_C1 = re.compile("[\udc80-\udc9f]")
ERRORS = "surrogateescape"


def check_encoding(encoding: object) -> Encoding:
    if encoding == "utf-8":
        return "utf-8"
    if encoding == "latin-1":
        return "latin-1"
    raise ValueError(f"encoding must be 'utf-8' or 'latin-1', not {encoding!r}")


def strip_control_bytes(
    data: bytes | bytearray | memoryview,
    *,
    keep: str = STANDARD_WHITESPACE,
    sequences: bool = True,
    format_chars: bool = False,
    encoding: Encoding = "utf-8",
) -> bytes:
    """Return ``data`` without control characters, as :func:`strip_control` does for text.

    With ``encoding="utf-8"`` a C1 control is the two-byte form ``C2 80`` to ``C2 9F``;
    bytes ``80`` to ``9F`` inside a valid character (``"Λ"`` is ``CE 9B``) are left
    alone. A stray byte ``80`` to ``9F`` outside any character is removed, since a terminal
    in 8-bit mode would act on it; other invalid bytes pass through unchanged. With
    ``encoding="latin-1"`` every byte ``80`` to ``9F`` is a C1 control.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError(f"data must be bytes, not {type(data).__name__}")
    check_text(keep, "keep")
    codec = check_encoding(encoding)
    text = bytes(data).decode(codec, ERRORS)
    if codec == "utf-8":
        text = STRAY_C1.sub("", text)
    clean = strip_control(text, keep=keep, sequences=sequences, format_chars=format_chars)
    return clean.encode(codec, ERRORS)
