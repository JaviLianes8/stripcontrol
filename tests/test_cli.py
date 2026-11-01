"""The command line as a stdin/stdout filter: modes, options, positions, pipes."""

from __future__ import annotations

import contextlib
import errno
import io
import types
from pathlib import Path

import pytest

from stripcontrol import _cli
from stripcontrol._cli import main

LOG = b"GET /\x1b]2;owned\x07 ok\nline \x1b[31mred\x1b[0m \xc2\x9b1m x\x9by \xce\x9b\n"


def _run(monkeypatch: pytest.MonkeyPatch, args: list[str], stdin: bytes = b"") -> tuple[int, bytes]:
    out = io.BytesIO()
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=io.BytesIO(stdin)))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=out))
    code = main(args)
    return code, out.getvalue()


def test_filter_strips_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = _run(monkeypatch, [], LOG)
    assert code == 0
    assert out == "GET / ok\nline red  xy Λ\n".encode()


def test_filter_reads_files_in_order(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    first, second = tmp_path / "a.log", tmp_path / "b.log"
    first.write_bytes(b"one\x1b]0;unterminated")
    second.write_bytes(b"two\x07\n")
    code, out = _run(monkeypatch, [str(first), "-", str(second)], b"mid\x00")
    # A sequence left open at the end of one file does not swallow the next one.
    assert (code, out) == (0, b"onemidtwo\n")


def test_a_sequence_split_across_reads_is_removed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_cli, "_CHUNK", 3)
    code, out = _run(monkeypatch, [], b"ab\x1b[38;5;196mc\xce\x9bd")
    assert (code, out) == (0, "abcΛd".encode())


def test_options(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _run(monkeypatch, ["--chars-only"], b"a\x1b[1mb")[1] == b"a[1mb"
    assert _run(monkeypatch, ["--strip-whitespace"], b"a\tb\n")[1] == b"ab"
    assert _run(monkeypatch, ["--format-chars"], "a\u202eb".encode())[1] == b"ab"
    assert _run(monkeypatch, ["--latin-1"], b"a\x9b1mb\xe9")[1] == b"ab\xe9"


def test_escape_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = _run(monkeypatch, ["--escape"], b"a\x1b[1m\tb\x9b\xc2\x85\xce\x9b\n")
    assert code == 0
    assert out == "a\\x1b[1m\tb\\x9b\\x85Λ\n".encode()


def test_check_mode_lists_positions_and_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(_cli, "_CHUNK", 5)
    code, out = _run(monkeypatch, ["--check"], LOG)
    assert code == 1
    assert out.decode().splitlines() == [
        "<stdin>:1:6: U+001B",
        "<stdin>:1:15: U+0007",
        "<stdin>:2:6: U+001B",
        "<stdin>:2:14: U+001B",
        "<stdin>:2:19: U+009B",
        "<stdin>:2:24: byte 0x9b",
    ]


def test_check_mode_passes_on_clean_input(monkeypatch: pytest.MonkeyPatch) -> None:
    assert _run(monkeypatch, ["--check"], "clean\ttext\n日本\n".encode()) == (0, b"")


def test_check_mode_honours_options(monkeypatch: pytest.MonkeyPatch) -> None:
    code, out = _run(monkeypatch, ["--check", "--strip-whitespace"], b"a\tb")
    assert (code, out) == (1, b"<stdin>:1:2: U+0009\n")
    code, out = _run(monkeypatch, ["--check", "--format-chars"], "\n\u2066".encode())
    assert (code, out) == (1, b"<stdin>:2:1: U+2066\n")


def test_a_missing_file_is_reported_and_the_rest_still_run(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    good = tmp_path / "good.log"
    good.write_bytes(b"ok\x00\n")
    code, out = _run(monkeypatch, [str(tmp_path / "missing.log"), str(good)])
    assert (code, out) == (2, b"ok\n")
    assert "missing.log" in capsys.readouterr().err


def test_check_and_escape_exclude_each_other(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(SystemExit) as exit_info:
        _run(monkeypatch, ["--check", "--escape"])
    assert exit_info.value.code == 2


class _ClosedPipe(io.BytesIO):
    def __init__(self, error: OSError) -> None:
        super().__init__()
        self.error = error

    def write(self, data: object) -> int:
        raise self.error


@pytest.mark.parametrize("error", [BrokenPipeError(), OSError(errno.EINVAL, "Invalid")])
def test_a_closed_pipe_ends_quietly(monkeypatch: pytest.MonkeyPatch, error: OSError) -> None:
    closed: list[bool] = []
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=io.BytesIO(b"text\n")))
    monkeypatch.setattr(
        "sys.stdout",
        types.SimpleNamespace(buffer=_ClosedPipe(error), close=lambda: closed.append(True)),
    )
    assert main([]) == 0
    assert closed == [True]


def test_other_write_errors_still_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=io.BytesIO(b"text\n")))
    full = _ClosedPipe(OSError(errno.ENOSPC, "No space left"))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=full))
    with pytest.raises(OSError, match="No space left"):
        main([])


def test_file_names_are_printed_escaped(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    evil = "x\x1b]2;t\x07.log"
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(io.BytesIO(b"\x00")))
    code, out = _run(monkeypatch, ["--check", evil])
    assert (code, out) == (1, b"x\\x1b]2;t\\x07.log:1:1: U+0000\n")
    monkeypatch.undo()
    code, out = _run(monkeypatch, [evil])
    assert (code, out) == (2, b"")
    assert capsys.readouterr().err.startswith("stripcontrol: x\\x1b]2;t\\x07.log: ")
