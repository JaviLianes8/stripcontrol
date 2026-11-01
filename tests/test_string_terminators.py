"""Handwritten string grammar cases, including kept and split terminators."""

from __future__ import annotations

import pickle
from typing import Literal

import pytest

from stripcontrol import ControlStripper, strip_control, strip_control_bytes

OPENERS = ["\x1b]", "\x9d", "\x1bP", "\x90", "\x1bX", "\x98", "\x1b^", "\x9e", "\x1b_", "\x9f"]


def _assert_splits(text: str, keep: str, expected: str) -> None:
    assert strip_control(text, keep=keep) == expected
    for cut in range(len(text) + 1):
        stream = ControlStripper(keep=keep)
        first = stream.feed(text[:cut])
        assert stream.feed("") == ""
        assert first + stream.feed(text[cut:]) + stream.close() == expected, cut
    stream = ControlStripper(keep=keep)
    assert "".join(stream.feed(char) for char in text) + stream.close() == expected


@pytest.mark.parametrize("opener", OPENERS)
@pytest.mark.parametrize("terminator", ["\x9c", "\x1b\\"])
@pytest.mark.parametrize("kept", [False, True])
def test_string_terminators_are_consumed_even_when_kept(
    opener: str, terminator: str, kept: bool
) -> None:
    keep = (terminator if "\x1b" not in opener else "\x9c") if kept else ""
    _assert_splits(f"a{opener}payload{terminator}visible", keep, "avisible")


@pytest.mark.parametrize("encoding", ["utf-8", "latin-1"])
@pytest.mark.parametrize("opener", OPENERS)
@pytest.mark.parametrize("terminator", ["\x9c", "\x1b\\"])
def test_byte_string_terminators_are_consumed(
    encoding: Literal["utf-8", "latin-1"], opener: str, terminator: str
) -> None:
    keep = terminator if "\x1b" not in opener else "\x9c"
    data = f"a{opener}payload{terminator}visible".encode(encoding)
    assert strip_control_bytes(data, keep=keep, encoding=encoding) == b"avisible"


@pytest.mark.parametrize("keep", ["", "\x1b"])
@pytest.mark.parametrize("tail", ["[31mvisible", "0visible", "\nvisible", "\x9b31mvisible"])
def test_nonterminating_escape_retains_cancellation_rules(keep: str, tail: str) -> None:
    expected = "a" + strip_control("\x1b" + tail, keep=keep)
    _assert_splits("a\x9dpayload\x1b" + tail, keep, expected)


def test_pending_kept_escape_is_dropped_on_close_and_survives_pickle() -> None:
    stream = ControlStripper(keep="\x1b")
    assert stream.feed("\x9dpayload\x1b") == ""
    assert stream.in_sequence
    restored = pickle.loads(pickle.dumps(stream))
    assert restored.feed("\\visible") == "visible"
    assert not restored.in_sequence
    assert stream.close() == "" and not stream.in_sequence
    assert stream.feed("\\visible") == "\\visible"


def test_terminators_outside_strings_and_character_only_mode_honor_keep() -> None:
    assert strip_control("\x9c\x1b\\", keep="\x9c\x1b") == "\x9c\x1b\\"
    assert strip_control("\x9dpayload\x1b\\", keep="\x1b", sequences=False) == "payload\x1b\\"
