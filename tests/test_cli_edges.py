"""Command line edge cases: read errors, joins across reads, names, flushing."""

from __future__ import annotations

import contextlib
import errno
import io
import types

import pytest

from stripcontrol import _cli
from stripcontrol._cli import main


class _Out(io.BytesIO):
    def __init__(self) -> None:
        super().__init__()
        self.flushes = 0

    def flush(self) -> None:
        self.flushes += 1


def _run(
    monkeypatch: pytest.MonkeyPatch, args: list[str], stdin: bytes = b""
) -> tuple[int, bytes, _Out]:
    out = _Out()
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=io.BytesIO(stdin)))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=out))
    code = main(args)
    return code, out.getvalue(), out


class _Failing(io.BytesIO):
    """Gives its data on the first read, then fails like a broken disk or pipe."""

    def __init__(self, data: bytes, error: OSError) -> None:
        super().__init__(data)
        self.error, self.reads = error, 0

    def read1(self, size: int | None = -1) -> bytes:
        self.reads += 1
        if self.reads > 1:
            raise self.error
        return super().read1(size)


@pytest.mark.parametrize("error", [OSError(errno.EIO, "I/O error"), OSError(errno.EINVAL, "bad")])
def test_a_read_error_is_reported_and_the_next_file_still_runs(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], error: OSError
) -> None:
    streams = {"bad": _Failing(b"one\x00", error), "good": io.BytesIO(b"two\x07\n")}
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(streams[name]))
    code, out, _ = _run(monkeypatch, ["bad", "good"])
    assert (code, out) == (2, b"onetwo\n")
    assert capsys.readouterr().err == f"stripcontrol: bad: {error.strerror}\n"


def test_a_read_error_in_check_mode_is_not_exit_1(monkeypatch: pytest.MonkeyPatch) -> None:
    failing = _Failing(b"ok\n", OSError(errno.EIO, "I/O error"))
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(failing))
    assert _run(monkeypatch, ["--check", "x"])[:2] == (2, b"")


def test_chars_only_is_refused_outside_strip_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    for mode in ("--check", "--escape"):
        with pytest.raises(SystemExit) as exit_info:
            _run(monkeypatch, [mode, "--chars-only"])
        assert exit_info.value.code == 2


def test_removal_does_not_join_bytes_across_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    for size in (1, 2, 3, 1 << 16):
        monkeypatch.setattr(_cli, "_CHUNK", size)
        data = b"a\xef\xbb\x00\xbfb\xef\xbb\x07\xef\xbb\x00\xbf\xbf"
        code, out, _ = _run(monkeypatch, ["--format-chars"], data)
        assert (code, out) == (0, b"a\xefb\xef\xbb\xef\xbf"), size


def test_an_incomplete_character_at_the_end_is_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _run(monkeypatch, [], b"a\xe2")[:2] == (0, b"a\xe2")
    assert _run(monkeypatch, ["--escape"], b"a\xe2")[:2] == (0, b"a\xe2")


def test_check_reports_a_control_and_a_stray_byte_in_one_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    code, out, _ = _run(monkeypatch, ["--check"], b"a\x9bb\x00")
    assert (code, out) == (1, b"<stdin>:1:2: byte 0x9b\n<stdin>:1:4: U+0000\n")


def test_undecodable_bytes_in_a_name_are_printed_escaped(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    name = "x\udc9b\ud800.log"
    monkeypatch.setattr(_cli, "_open", lambda _: contextlib.nullcontext(io.BytesIO(b"\x00")))
    code, out, _ = _run(monkeypatch, ["--check", name])
    assert (code, out) == (1, b"x\\x9b\\ud800.log:1:1: U+0000\n")


def test_every_piece_is_flushed_for_live_streams(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_cli, "_CHUNK", 2)
    code, out, stream = _run(monkeypatch, [], b"abcdef")
    assert (code, out) == (0, b"abcdef")
    assert stream.flushes >= 3
