"""Handwritten contracts for stream reuse, escape boundaries and exact codec names."""

from __future__ import annotations

from typing import Literal

import pytest

from stripcontrol import ControlStripper, strip_control, strip_control_bytes


@pytest.mark.parametrize(
    ("keep", "sequences", "format_chars", "text", "expected"),
    [
        ("", True, False, "a\tb", "ab"),
        ("\t\n\r", False, False, "a\x1b[31mb", "a[31mb"),
        ("\t\n\r", True, True, "a\u202eb", "ab"),
        ("", False, True, "a\t\x1b[31m\u202eb", "a[31mb"),
    ],
)
def test_close_preserves_every_option_across_reuse(
    keep: str, sequences: bool, format_chars: bool, text: str, expected: str
) -> None:
    stream = ControlStripper(keep=keep, sequences=sequences, format_chars=format_chars)
    for _ in range(3):
        assert stream.feed(text) == expected
        if sequences:
            assert stream.feed("\x1b[") == "" and stream.in_sequence
        assert stream.close() == ""
        assert stream.close() == ""
        assert not stream.in_sequence


def test_first_final_byte_directly_after_escape_at_every_split() -> None:
    text = "x\x1b0y"
    assert strip_control(text) == "xy"
    for cut in range(len(text) + 1):
        stream = ControlStripper()
        assert stream.feed(text[:cut]) + stream.feed(text[cut:]) + stream.close() == "xy"
    stream = ControlStripper()
    assert "".join(stream.feed(char) for char in text) + stream.close() == "xy"


@pytest.mark.parametrize("encoding", ["utf-8", "latin-1"])
def test_supported_encoding_names(encoding: Literal["utf-8", "latin-1"]) -> None:
    assert strip_control_bytes(b"a\x00b", encoding=encoding) == b"ab"


@pytest.mark.parametrize(
    "encoding",
    ["utf8", "UTF-8", "utf_8", "latin1", "LATIN-1", "latin_1", "iso-8859-1", "ascii", ""],
)
def test_encoding_aliases_are_rejected(encoding: str) -> None:
    with pytest.raises(ValueError, match=r"^encoding must be 'utf-8' or 'latin-1'$"):
        strip_control_bytes(b"x", encoding=encoding)  # type: ignore[arg-type]
