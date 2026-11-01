"""Wrong input types must not execute their inspection or conversion hooks."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from stripcontrol import (
    ControlStripper,
    escape_control,
    find_control,
    has_control,
    strip_control,
    strip_control_bytes,
)


class _Pretender:
    @property  # type: ignore[misc]
    def __class__(self) -> type[object]:  # type: ignore[override]
        raise AssertionError("input inspection is forbidden")

    def __bool__(self) -> bool:
        raise AssertionError("input truth conversion is forbidden")


@pytest.mark.parametrize("call", [strip_control, has_control, find_control, escape_control])
def test_text_operations_reject_type_hooks(call: Callable[..., object]) -> None:
    with pytest.raises(TypeError, match="text must be str"):
        call(_Pretender())
    with pytest.raises(TypeError, match="keep must be str"):
        call("", keep=_Pretender())
    with pytest.raises(TypeError, match="format_chars must be bool"):
        call("", format_chars=_Pretender())


def test_stream_rejects_type_hooks_without_changing_state() -> None:
    stream = ControlStripper()
    stream.feed("\x1b[")
    with pytest.raises(TypeError):
        stream.feed(_Pretender())  # type: ignore[arg-type]
    assert stream.in_sequence
    assert stream.feed("31mtext") == "text"
    with pytest.raises(TypeError, match="sequences must be bool"):
        ControlStripper(sequences=_Pretender())  # type: ignore[arg-type]


def test_bytes_reject_type_hooks() -> None:
    with pytest.raises(TypeError, match="data must be bytes"):
        strip_control_bytes(_Pretender())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="encoding must be str"):
        strip_control_bytes(b"", encoding=_Pretender())  # type: ignore[arg-type]
