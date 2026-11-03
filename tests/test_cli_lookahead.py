"""Leads the real CLI decoder keeps pending: a lead that cannot complete is written at once."""

from __future__ import annotations

import contextlib
import errno
import io
import types

import pytest

from stripcontrol import _cli
from stripcontrol._cli import main

# Each tail is a lead followed by a byte the incremental decoder keeps in its own buffer:
# another lead, or A0..BF after ED (a surrogate, never a character in UTF-8).
_PENDING = {
    b"\xc2\xc2": b"\xc2",
    b"\xe0\xf0": b"\xe0",
    b"\xf4\xc2": b"\xf4",
    b"\xed\xa0": b"\xed\xa0",
    b"\xed\xbf": b"\xed\xbf",
}


class _Stream(io.BytesIO):
    """Gives ``data`` on the first read; the next read records the output so far, then fails."""

    def __init__(self, data: bytes, out: io.BytesIO) -> None:
        super().__init__(data)
        self.out = out
        self.seen: bytes | None = None

    def read1(self, size: int | None = -1) -> bytes:
        if self.seen is not None:
            raise OSError(errno.EIO, "read failure")
        data = super().read1(size)
        if not data:
            self.seen = self.out.getvalue()
            raise OSError(errno.EIO, "read failure")
        return data


def _run(monkeypatch: pytest.MonkeyPatch, data: bytes) -> tuple[int, bytes | None, bytes]:
    out = io.BytesIO()
    stream = _Stream(data, out)
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(stream))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=out))
    status = main(["in"])
    return status, stream.seen, out.getvalue()


@pytest.mark.parametrize("tail", sorted(_PENDING), ids=lambda tail: tail.hex())
def test_a_live_stream_writes_a_lead_its_pending_byte_cannot_continue(
    monkeypatch: pytest.MonkeyPatch, tail: bytes
) -> None:
    # What a reader sees while stdin stays open, before the next read returns.
    assert _run(monkeypatch, b"a" + tail)[1] == b"a" + _PENDING[tail]


@pytest.mark.parametrize("tail", sorted(_PENDING), ids=lambda tail: tail.hex())
def test_a_read_failure_keeps_a_lead_its_pending_byte_cannot_continue(
    monkeypatch: pytest.MonkeyPatch, tail: bytes
) -> None:
    assert _run(monkeypatch, b"a" + tail)[::2] == (2, b"a" + _PENDING[tail])


def _completes(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _can_complete(data: bytes) -> bool:
    """Whether continuation bytes complete ``data``, checked by the strict decoder."""
    if _completes(data):
        return False
    seconds = range(0x80, 0xC0) if len(data) == 1 else [None]
    for second in seconds:
        head = data if second is None else data + bytes([second])
        if any(_completes(head + b"\x80" * extra) for extra in range(3)):
            return True
    return False


def test_every_lead_pair_loses_only_bytes_that_can_still_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    wrong = []
    for lead in range(0xC2, 0xF5):
        for second in range(0xA0, 0x100):
            data = b"a" + bytes([lead, second])
            expected = data
            for size in (2, 1):
                if _can_complete(data[-size:]):
                    expected = data[:-size]
                    break
            if _run(monkeypatch, data)[1:] != (expected, expected):
                wrong.append(data.hex(" "))
    assert wrong == []


class _Reads(io.BytesIO):
    def __init__(self, reads: list[bytes]) -> None:
        super().__init__()
        self.reads = reads

    def read1(self, size: int | None = -1) -> bytes:
        return self.reads.pop(0) if self.reads else b""


def test_pending_bytes_after_an_open_sequence_are_not_lookahead(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The pending C2 80 ends the ESC and is removed, so the lead meets BF from the next read.
    out = io.BytesIO()
    stream = _Reads([b"a\xc2\x1b\xc2", b"\x80\xbf"])
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(stream))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=out))
    assert (main(["in"]), out.getvalue()) == (0, b"a\xc2")
