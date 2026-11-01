"""Bounded diagnostics, seeded binary streaming, and arbitrary stream boundaries."""

from __future__ import annotations

import errno
import io
import random
import types

import pytest

from stripcontrol import _cli, strip_control_bytes
from stripcontrol._cli_errors import shown


def test_usage_error_does_not_echo_argument_values(capsys: pytest.CaptureFixture[str]) -> None:
    secret = "secret" * 10000 + "\x1b[31m"
    with pytest.raises(SystemExit) as error:
        _cli.main(["--" + secret])
    assert error.value.code == 2
    diagnostic = capsys.readouterr().err
    assert "secret" not in diagnostic and "\x1b" not in diagnostic
    assert len(diagnostic) < 500


def test_input_error_does_not_echo_os_error_payload(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def fail(name: str) -> None:
        raise OSError(errno.EIO, "secret" * 10000)

    monkeypatch.setattr(_cli, "_open", fail)
    assert _cli.main(["x" * 10000 + "\x1b"]) == 2
    diagnostic = capsys.readouterr().err
    assert "secret" not in diagnostic and "\x1b" not in diagnostic
    assert len(diagnostic) < 200


def test_file_labels_are_bounded_after_escaping() -> None:
    assert shown("a" * 120) == "a" * 120
    assert shown("a" * 121) == "a" * 120 + "..."
    assert shown("\x1b" * 31) == "\\x1b" * 30 + "..."


def test_seeded_cli_stripping_matches_the_bytes_api(monkeypatch: pytest.MonkeyPatch) -> None:
    rng = random.Random(20261101)
    for _ in range(400):
        data = bytes(rng.randrange(256) for _ in range(rng.randrange(180)))
        data += rng.choice([b"\xef\xbb\x00\xbf", b"\x1b[31m", b"\xf0\xa0\x00\xa0\xa0"])
        size = rng.randrange(1, 12)
        monkeypatch.setattr(_cli, "_CHUNK", size)
        output = io.BytesIO()
        monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=io.BytesIO(data)))
        monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=output))
        flags = rng.choice(
            [[], ["--format-chars"], ["--strip-whitespace"], ["--chars-only"], ["--latin-1"]]
        )
        assert _cli.main(flags) == 0
        expected = strip_control_bytes(
            data,
            keep="" if "--strip-whitespace" in flags else "\t\n\r",
            sequences="--chars-only" not in flags,
            format_chars="--format-chars" in flags,
            encoding="latin-1" if "--latin-1" in flags else "utf-8",
        )
        assert output.getvalue() == expected, (data, size, flags)
