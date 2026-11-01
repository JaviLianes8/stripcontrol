"""Stable signatures, errors, buffers and stream state through the public imports."""

from __future__ import annotations

import array
import inspect
import pickle
from collections.abc import Callable, Iterator
from typing import cast, get_type_hints

import pytest

import stripcontrol as sc

TEXT_CALLS = [sc.strip_control, sc.has_control, sc.find_control, sc.escape_control]


@pytest.mark.parametrize("call", TEXT_CALLS)
def test_text_signatures_and_defaults(call: Callable[..., object]) -> None:
    parameters = inspect.signature(call).parameters
    names = ["text", "keep", "format_chars"]
    if call is sc.strip_control:
        names.insert(2, "sequences")
    assert list(parameters) == names
    assert parameters["text"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["keep"].default == "\t\n\r"
    assert parameters["format_chars"].default is False
    for name in names[1:]:
        assert parameters[name].kind == inspect.Parameter.KEYWORD_ONLY
    if "sequences" in parameters:
        assert parameters["sequences"].default is True
    assert get_type_hints(call)


def test_bytes_and_stream_signatures_are_stable() -> None:
    parameters = inspect.signature(sc.strip_control_bytes).parameters
    assert list(parameters) == ["data", "keep", "sequences", "format_chars", "encoding"]
    assert parameters["encoding"].default == "utf-8"
    assert parameters["keep"].default == "\t\n\r"
    assert parameters["sequences"].default is True
    assert parameters["format_chars"].default is False
    assert list(inspect.signature(sc.ControlStripper).parameters) == [
        "keep",
        "sequences",
        "format_chars",
    ]
    assert sc.ControlStripper.__module__ == "stripcontrol"


@pytest.mark.parametrize("call", TEXT_CALLS)
@pytest.mark.parametrize("bad", [None, 1, b"secret", [], object()])
def test_text_errors_have_fixed_messages(call: Callable[..., object], bad: object) -> None:
    with pytest.raises(TypeError) as error:
        call(bad)
    assert str(error.value) == "text must be str"
    with pytest.raises(TypeError) as error:
        call("", keep=bad)
    assert str(error.value) == "keep must be str"


@pytest.mark.parametrize("call", [*TEXT_CALLS, sc.ControlStripper, sc.strip_control_bytes])
@pytest.mark.parametrize("bad", [0, 1, None, "secret", [], object()])
def test_boolean_options_reject_non_booleans(call: Callable[..., object], bad: object) -> None:
    args: tuple[object, ...] = () if call is sc.ControlStripper else ("",)
    if call is sc.strip_control_bytes:
        args = (b"",)
    for option in ("sequences", "format_chars"):
        if option not in inspect.signature(call).parameters:
            continue
        with pytest.raises(TypeError) as error:
            call(*args, **{option: bad})
        assert str(error.value) == f"{option} must be bool"


def test_encoding_errors_never_format_the_value() -> None:
    class Bad:
        def __repr__(self) -> str:
            raise AssertionError("input must not be formatted")

    with pytest.raises(TypeError, match=r"^encoding must be str$"):
        sc.strip_control_bytes(b"", encoding=cast("str", Bad()))  # type: ignore[arg-type]
    with pytest.raises(ValueError) as error:
        sc.strip_control_bytes(b"", encoding="secret" * 100_000)  # type: ignore[arg-type]
    assert str(error.value) == "encoding must be 'utf-8' or 'latin-1'"


def test_buffers_use_raw_bytes_and_do_not_mutate_input() -> None:
    raw = bytearray(b"a\x00b\x00c\x00")
    assert sc.strip_control_bytes(memoryview(raw)[::2]) == b"abc"
    wide = array.array("H", [0x0061, 0x0062])
    expected = bytes(wide).replace(b"\x00", b"")
    assert sc.strip_control_bytes(memoryview(wide)) == expected
    assert raw == bytearray(b"a\x00b\x00c\x00")
    view = memoryview(raw)
    view.release()
    with pytest.raises(ValueError):
        sc.strip_control_bytes(view)


def test_subclasses_are_read_without_overridable_conversion() -> None:
    class Text(str):
        def __str__(self) -> str:
            return "wrong"

        def __iter__(self) -> Iterator[str]:
            raise AssertionError("iteration hook")

    class Buffer(bytes):
        def __bytes__(self) -> bytes:
            return b"wrong"

    assert sc.strip_control(Text("a\x00b"), keep=Text("\n")) == "ab"
    assert sc.has_control(Text("\x00"))
    assert sc.find_control(Text("\x00")) == [(0, 0)]
    assert sc.escape_control(Text("\x00")) == "\\x00"
    assert sc.strip_control_bytes(Buffer(b"a\x00b")) == b"ab"


@pytest.mark.parametrize("prefix", ["\x1b", "\x1b(", "\x1b[", "\x9d", "\x90"])
def test_stream_empty_feeds_rejection_pickle_and_reset(prefix: str) -> None:
    stream = sc.ControlStripper()
    assert stream.feed(prefix) == "" and stream.in_sequence is True
    assert stream.feed("") == "" and stream.in_sequence is True
    with pytest.raises(TypeError):
        stream.feed(b"bad")  # type: ignore[arg-type]
    assert stream.in_sequence is True
    restored = pickle.loads(pickle.dumps(stream))
    assert restored.feed("\x18tail") == "tail"
    assert stream.close() == "" and stream.close() == ""
    assert stream.in_sequence is False and stream.feed("tail") == "tail"
