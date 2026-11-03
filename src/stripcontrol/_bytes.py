"""Strip bytes: C1 as two UTF-8 bytes (C2 80..C2 9F) or as one 8-bit byte (80..9F)."""

from __future__ import annotations

import re
from typing import Literal, cast

from ._control import STANDARD_WHITESPACE
from ._stripper import strip_control

Encoding = Literal["utf-8", "latin-1"]

# Undecodable bytes travel as lone surrogates U+DC80..U+DCFF (PEP 383). Those standing for
# a stray byte 80..9F are what an 8-bit terminal would run as a C1 control.
STRAY_C1 = re.compile("[\udc80-\udc9f]")
ERRORS = "surrogateescape"
_ESCAPED = re.compile("[\udc80-\udcff]")


def check_encoding(encoding: object) -> Encoding:
    if not issubclass(type(encoding), str):
        raise TypeError("encoding must be str")
    encoding = str.__str__(encoding)
    if encoding == "utf-8":
        return "utf-8"
    if encoding == "latin-1":
        return "latin-1"
    raise ValueError("encoding must be 'utf-8' or 'latin-1'")


def _continuations(char: str) -> int:
    """How many continuation bytes an escaped UTF-8 lead byte asks for (0: not a lead)."""
    byte = ord(char) - 0xDC00
    if 0xC2 <= byte <= 0xDF:
        return 1
    if 0xE0 <= byte <= 0xEF:
        return 2
    return 3 if 0xF0 <= byte <= 0xF4 else 0


# Bytes allowed right after these leads (RFC 3629, section 4); otherwise 80..BF.
_SECOND = {0xE0: (0xA0, 0xBF), 0xED: (0x80, 0x9F), 0xF0: (0x90, 0xBF), 0xF4: (0x80, 0x8F)}


def _can_continue(char: str, tail: str) -> bool:
    """Whether more continuation bytes could still turn ``char + tail`` into a character."""
    for index, item in enumerate(tail):
        low, high = _SECOND.get(ord(char) - 0xDC00, (0x80, 0xBF)) if index == 0 else (0x80, 0xBF)
        if not low <= ord(item) - 0xDC00 <= high:
            return False
    return True


def can_complete(chars: str) -> bool:
    """Whether escaped ``chars`` are a lead byte that continuation bytes could still complete."""
    need = _continuations(chars[0]) if chars and _ESCAPED.match(chars[0]) else 0
    return len(chars) <= need and _can_continue(chars[0], chars[1:])


def _forms_a_character(chars: str) -> bool:
    try:
        bytes(ord(char) - 0xDC00 for char in chars).decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def unjoin(text: str, final: bool = True, after: str = "") -> tuple[str, str]:
    """Drop escaped bytes that removal has joined into a valid UTF-8 character.

    Removing ``00`` from ``EF BB 00 BF`` would leave ``EF BB BF``, a byte order mark. Such
    bytes were invalid where they stood, so the continuation bytes are dropped instead of
    letting them form a character nobody checked. Returns the safe text and, unless
    ``final``, a held-back tail (at most four characters) to prefix to the next chunk. Only
    a lead byte followed by bytes that can still complete it is held back; ``after`` holds
    escaped bytes known to come next (a decoder's pending bytes) and is only looked at.
    """
    if _ESCAPED.search(text) is None:
        return text, ""
    out: list[str] = []
    pos, end = 0, len(text)
    while pos < end:
        char = text[pos]
        pos += 1
        need = _continuations(char) if _ESCAPED.match(char) else 0
        while need:
            tail = text[pos : pos + need]
            escaped = all(_ESCAPED.match(item) for item in tail)
            # Only bytes that can still become a character are worth holding back.
            ahead = (tail + after)[:need]
            if escaped and len(tail) < need and not final and _can_continue(char, ahead):
                return "".join(out), char + text[pos:]
            if not (escaped and len(tail) == need and _forms_a_character(char + tail)):
                break
            pos += need
        out.append(char)
    return "".join(out), ""


def strip_control_bytes(
    data: bytes | bytearray | memoryview,
    *,
    keep: str = STANDARD_WHITESPACE,
    sequences: bool = True,
    format_chars: bool = False,
    encoding: Encoding = "utf-8",
) -> bytes:
    r"""Return ``data`` without control characters, as :func:`strip_control` does for text.

    With ``encoding="utf-8"`` a C1 control is the two-byte form ``C2 80`` to ``C2 9F``;
    bytes ``80`` to ``9F`` inside a valid character (``"Λ"`` is ``CE 9B``) are left
    alone. A stray byte ``80`` to ``9F`` outside any character is removed, since a terminal
    in 8-bit mode would act on it; other invalid bytes pass through unchanged unless a
    removal would join them into a character. With ``encoding="latin-1"`` every byte
    ``80`` to ``9F`` is a C1 control. ``keep`` is text, so it cannot keep a stray byte.
    Invalid argument types raise TypeError; unsupported encodings and released
    memoryviews raise ValueError. Memoryviews are read as raw bytes in logical order.

    >>> from stripcontrol import strip_control_bytes
    >>> strip_control_bytes(b"a\x1b[31mb\x00")
    b'ab'
    """
    if not issubclass(type(data), (bytes, bytearray, memoryview)):
        raise TypeError("data must be bytes, bytearray or memoryview")
    codec = check_encoding(encoding)
    if issubclass(type(data), bytes):
        data = bytes.__getitem__(cast(bytes, data), slice(None))
    elif issubclass(type(data), bytearray):
        data = bytearray.__getitem__(cast(bytearray, data), slice(None))
    text = memoryview(data).tobytes().decode(codec, ERRORS)
    if codec == "utf-8":
        text = STRAY_C1.sub("", text)
    clean = strip_control(text, keep=keep, sequences=sequences, format_chars=format_chars)
    if codec == "utf-8":
        clean = unjoin(clean)[0]
    return clean.encode(codec, ERRORS)
