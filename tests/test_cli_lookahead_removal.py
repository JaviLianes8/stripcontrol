"""Pending bytes that the stripper removes must not let a written lead join later bytes."""

from __future__ import annotations

import contextlib
import io
import types

import pytest

from stripcontrol import _cli, strip_control_bytes
from stripcontrol._cli import main
from stripcontrol._format_table import FORMAT_RANGES

_OPTIONS = {
    "": [],
    "format": ["--format-chars"],
    "whitespace": ["--strip-whitespace"],
    "chars-only": ["--chars-only"],
    "format-whitespace": ["--format-chars", "--strip-whitespace"],
}


def _keywords(flags: list[str]) -> dict[str, object]:
    return {
        "keep": "" if "--strip-whitespace" in flags else "\t\n\r",
        "sequences": "--chars-only" not in flags,
        "format_chars": "--format-chars" in flags,
    }


class _Reads(io.BytesIO):
    def __init__(self, reads: list[bytes]) -> None:
        super().__init__()
        self.reads = reads

    def read1(self, size: int | None = -1) -> bytes:
        return self.reads.pop(0) if self.reads else b""


def _cli_output(monkeypatch: pytest.MonkeyPatch, reads: list[bytes], flags: list[str]) -> bytes:
    out = io.BytesIO()
    stream = _Reads(list(reads))
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(stream))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=out))
    assert main([*flags, "in"]) == 0
    return out.getvalue()


@pytest.mark.parametrize(
    ("first", "second", "flags", "expected"),
    [
        (b"a\xc2\xc2", b"\x80\xbf", [], b"a\xc2"),
        (b"a\xe0\xc2", b"\x80\xa0\xa0", [], b"a\xe0"),
        (b"a\xc2\xe2", b"\x80\x8b\xbf", ["--format-chars"], b"a\xc2"),
        (b"a\xe0\xa0\xc2", b"\x80\xa0", [], b"a\xe0"),
        (b"a\xe0\xa0\xe2", b"\x80\x8b\xa0", ["--format-chars"], b"a\xe0"),
    ],
    ids=["c1-joins-c2-bf", "c1-joins-u0820", "zwsp-joins-c2-bf", "c1-tail", "zwsp-tail"],
)
def test_a_removed_pending_character_does_not_join_the_written_lead(
    monkeypatch: pytest.MonkeyPatch, first: bytes, second: bytes, flags: list[str], expected: bytes
) -> None:
    whole = first + second
    assert strip_control_bytes(whole, **_keywords(flags)) == expected  # type: ignore[arg-type]
    assert _cli_output(monkeypatch, [first, second], flags) == expected
    assert _cli_output(monkeypatch, [whole], flags) == expected


def _removable(flags: list[str]) -> list[bytes]:
    codes = list(range(0x80, 0xA0))
    if "--format-chars" in flags:
        codes += [code for start, end in FORMAT_RANGES for code in range(start, end + 1)]
    return [chr(code).encode("utf-8") for code in codes]


_FILLS = (b"\xbf\xbf\xbf", b"\x80\x80\x80", b"\xa0\xa0\xa0", b"\x90\x90\x90")


@pytest.mark.parametrize("name", sorted(_OPTIONS))
def test_two_reads_end_as_one_strip_for_every_lead_and_pending_byte(
    monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    flags = _OPTIONS[name]
    keywords = _keywords(flags)
    removable = _removable(flags)
    wrong = []
    for lead in range(0xC2, 0xF5):
        for pending in range(0xC2, 0xF5):
            rests = [char[1:] for char in removable if char[0] == pending]
            rests = sorted(set(rests[:1] + rests[-1:])) or [b"\xbf"]
            first = bytes([ord("a"), lead, pending])
            for rest in rests:
                for fill in _FILLS:
                    second = rest + fill
                    expected = strip_control_bytes(first + second, **keywords)  # type: ignore[arg-type]
                    if _cli_output(monkeypatch, [first, second], flags) != expected:
                        wrong.append((first + b"|" + second).hex(" "))
    assert wrong == []
