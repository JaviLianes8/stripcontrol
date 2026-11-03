"""A lead written through lookahead must stay context across more than one later read."""

from __future__ import annotations

import contextlib
import io
import itertools
import random
import types

import pytest

from stripcontrol import _cli, strip_control_bytes
from stripcontrol._cli import main
from stripcontrol._format_table import FORMAT_RANGES

_FLAGS = ("--format-chars", "--strip-whitespace", "--chars-only", "--latin-1")
_OPTION_SETS = [
    [flag for flag, on in zip(_FLAGS, mask, strict=True) if on]
    for mask in itertools.product((False, True), repeat=len(_FLAGS))
]


def _keywords(flags: list[str]) -> dict[str, object]:
    return {
        "keep": "" if "--strip-whitespace" in flags else "\t\n\r",
        "sequences": "--chars-only" not in flags,
        "format_chars": "--format-chars" in flags,
        "encoding": "latin-1" if "--latin-1" in flags else "utf-8",
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
    ("reads", "flags", "expected"),
    [
        ([b"\xf0\xc2", b"\x9b\xa0\xbb", b"\xa0"], [], b"\xf0"),
        (
            [b"\x8b", b"\xc2\xc2\xe2", b"\x80\x8b\xc2\x85", b"\xbb\x80\xf4"],
            ["--format-chars", "--strip-whitespace"],
            b"\xc2\xc2\xf4",
        ),
    ],
    ids=["c1-pending-then-two-reads", "zwsp-pending-then-two-reads"],
)
def test_a_written_lead_stays_context_over_later_reads(
    monkeypatch: pytest.MonkeyPatch, reads: list[bytes], flags: list[str], expected: bytes
) -> None:
    whole = b"".join(reads)
    assert strip_control_bytes(whole, **_keywords(flags)) == expected  # type: ignore[arg-type]
    assert _cli_output(monkeypatch, reads, flags) == expected


def _alphabet() -> list[bytes]:
    pieces = [bytes([code]) for code in range(0x80, 0xC0, 3)]  # continuations, stray C1
    pieces += [bytes([code]) for code in (0xC2, 0xE0, 0xE2, 0xED, 0xEF, 0xF0, 0xF4, 0xF5)]
    pieces += [chr(code).encode("utf-8") for code in range(0x80, 0xA0, 5)]  # C1 controls
    pieces += [chr(code).encode("utf-8") for start, _ in FORMAT_RANGES[:6] for code in [start]]
    pieces += [b"a", b"\t", b"\n", b"\x1b", b"\x1b[", b"\x07", b"\x00", b"[1m"]
    return pieces


def test_random_reads_end_as_one_strip_for_every_option_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rng = random.Random(20261103)
    alphabet = _alphabet()
    wrong = []
    for _ in range(250):
        data = b"".join(rng.choices(alphabet, k=rng.randint(1, 12)))
        cuts = sorted(rng.sample(range(1, len(data) + 1), min(len(data), rng.randint(1, 3))))
        bounds = zip([0, *cuts], [*cuts, len(data)], strict=True)
        reads = [data[start:stop] for start, stop in bounds if start < stop]
        for flags in _OPTION_SETS:
            expected = strip_control_bytes(data, **_keywords(flags))  # type: ignore[arg-type]
            if _cli_output(monkeypatch, reads, flags) != expected:
                wrong.append((" ".join(flags), b"|".join(reads).hex(" ")))
    assert wrong == []
