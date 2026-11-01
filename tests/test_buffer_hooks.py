"""Byte subclasses must use stored contents without executing user hooks."""

from __future__ import annotations

import contextlib
from typing import Literal, NoReturn

import pytest

from stripcontrol import strip_control_bytes


@pytest.mark.parametrize("base", [bytes, bytearray])
@pytest.mark.parametrize("action", ["replace", "runtime", "large_error"])
@pytest.mark.parametrize("encoding", ["utf-8", "latin-1"])
def test_byte_subclasses_ignore_buffer_and_content_hooks(
    base: type[bytes] | type[bytearray], action: str, encoding: Literal["utf-8", "latin-1"]
) -> None:
    calls: list[str] = []

    def buffer_hook(self: object, flags: int) -> memoryview:
        calls.append("buffer")
        if action == "runtime":
            raise RuntimeError("private marker")
        if action == "large_error":
            raise ValueError("private marker" * 100_000)
        return memoryview(b"forged")

    def forbidden(*args: object) -> NoReturn:
        calls.append("content")
        raise AssertionError("content hook must not run")

    hostile = type(
        "Hostile",
        (base,),
        {
            "__buffer__": buffer_hook,
            "__bytes__": forbidden,
            "__getitem__": forbidden,
            "__iter__": forbidden,
            "__len__": forbidden,
        },
    )
    data = hostile(b"a\x00b")
    result: bytes | None = None
    with contextlib.suppress(RuntimeError, ValueError, AssertionError):
        result = strip_control_bytes(data, encoding=encoding)
    assert calls == []
    assert result == b"ab"
    assert base.__getitem__(data, slice(None)) == b"a\x00b"
