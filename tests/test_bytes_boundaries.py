"""UTF-8 lead and continuation byte boundaries: what the joining protection may hold back."""

from __future__ import annotations

import contextlib
import errno
import io
import types

import pytest

from stripcontrol import _cli, strip_control_bytes
from stripcontrol._bytes import ERRORS, unjoin
from stripcontrol._cli import main

# Handwritten from the UTF8-octets grammar of RFC 3629, section 4
# (https://www.rfc-editor.org/rfc/rfc3629#section-4): continuation bytes for each lead
# and the range allowed for the byte right after it. Later bytes are always 80..BF.
_RFC3629 = {
    **{lead: (1, 0x80, 0xBF) for lead in range(0xC2, 0xE0)},
    0xE0: (2, 0xA0, 0xBF),
    **{lead: (2, 0x80, 0xBF) for lead in (*range(0xE1, 0xED), 0xEE, 0xEF)},
    0xED: (2, 0x80, 0x9F),
    0xF0: (3, 0x90, 0xBF),
    0xF1: (3, 0x80, 0xBF),
    0xF2: (3, 0x80, 0xBF),
    0xF3: (3, 0x80, 0xBF),
    0xF4: (3, 0x80, 0x8F),
}
_LEADS = sorted(_RFC3629)


def _esc(*values: int) -> str:
    return "".join(chr(0xDC00 + value) for value in values)


def _completes(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _prefix(data: bytes) -> bool:
    """Whether some continuation bytes complete ``data``, checked by the strict decoder."""
    seconds = range(0x80, 0xC0) if len(data) == 1 else [None]
    for second in seconds:
        head = data if second is None else data + bytes([second])
        if any(_completes(head + bytes([0x80]) * extra) for extra in range(3)):
            return True
    return False


def _rest(text: str) -> tuple[str, str]:
    """Nothing before the last byte is held; the last byte is held only if it is a lead."""
    if ord(text[-1]) - 0xDC00 in _RFC3629:
        return text[:-1], text[-1]
    return text, ""


def test_the_handwritten_table_matches_an_independent_decoder() -> None:
    for byte in range(0x80, 0x100):
        assert (byte in _RFC3629) == _prefix(bytes([byte])), hex(byte)
    for lead, (_, low, high) in _RFC3629.items():
        for second in range(0x80, 0x100):
            assert (low <= second <= high) == _prefix(bytes([lead, second])), hex(second)


@pytest.mark.parametrize("byte", range(0x80, 0x100), ids=lambda byte: f"{byte:02x}")
def test_only_a_lead_byte_is_held_back_at_the_end(byte: int) -> None:
    text = "a" + _esc(byte)
    held = ("a", _esc(byte)) if byte in _RFC3629 else (text, "")
    assert unjoin(text, final=False) == held
    assert unjoin(text) == (text, "")


@pytest.mark.parametrize("lead", _LEADS, ids=lambda byte: f"{byte:02x}")
def test_a_lead_is_held_only_while_its_next_byte_can_continue_it(lead: int) -> None:
    need, low, high = _RFC3629[lead]
    for second in range(0x80, 0x100):
        text = _esc(lead, second)
        if need > 1 and low <= second <= high:
            assert unjoin(text, final=False) == ("", text), hex(second)
        elif low <= second <= high:
            # A complete character of escaped bytes: the continuation is dropped and the
            # lead is held again in case more removed bytes would join it.
            assert unjoin(text, final=False) == ("", _esc(lead)), hex(second)
            assert unjoin(text) == (_esc(lead), ""), hex(second)
        else:
            assert unjoin(text, final=False) == _rest(text), hex(second)


@pytest.mark.parametrize("lead", [lead for lead in _LEADS if _RFC3629[lead][0] > 1])
def test_later_bytes_must_be_continuations_to_be_held(lead: int) -> None:
    need, low, _ = _RFC3629[lead]
    for later in range(0x80, 0x100):
        for start in ((low,), (low, 0x80))[: need - 1]:
            text = _esc(lead, *start, later)
            if 0x80 <= later <= 0xBF and len(start) + 1 < need:
                assert unjoin(text, final=False) == ("", text), hex(later)
            elif 0x80 <= later <= 0xBF:
                assert unjoin(text, final=False) == ("", _esc(lead)), hex(later)
            else:
                assert unjoin(text, final=False) == _rest(text), hex(later)


@pytest.mark.parametrize("lead", _LEADS, ids=lambda byte: f"{byte:02x}")
def test_a_lead_joined_with_exactly_its_continuations_loses_them(lead: int) -> None:
    need, low, _ = _RFC3629[lead]
    whole = _esc(lead, low, *[0x80] * (need - 1))
    assert unjoin(whole) == (_esc(lead), "")
    assert unjoin(whole[:-1]) == (whole[:-1], "")
    assert unjoin(whole[:-1], final=False) == ("", whole[:-1])


@pytest.mark.parametrize("byte", range(0x80, 0x100), ids=lambda byte: f"{byte:02x}")
def test_one_stray_byte_is_removed_only_in_the_c1_range(byte: int) -> None:
    data = b"a" + bytes([byte]) + b"z"
    assert strip_control_bytes(data) == (b"az" if byte <= 0x9F else data)


class _Failing(io.BytesIO):
    def __init__(self, data: bytes) -> None:
        super().__init__(data)
        self.reads = 0

    def read1(self, size: int | None = -1) -> bytes:
        self.reads += 1
        if self.reads > 1:
            raise OSError(errno.EIO, "read failure")
        return super().read1(size)


def _failed_read(monkeypatch: pytest.MonkeyPatch, data: bytes) -> tuple[int, bytes]:
    out = io.BytesIO()
    monkeypatch.setattr(_cli, "_open", lambda name: contextlib.nullcontext(_Failing(data)))
    monkeypatch.setattr("sys.stdout", types.SimpleNamespace(buffer=out))
    return main(["bad"]), out.getvalue()


@pytest.mark.parametrize("byte", range(0xA0, 0x100), ids=lambda byte: f"{byte:02x}")
def test_a_read_failure_loses_only_a_byte_that_can_still_complete(
    monkeypatch: pytest.MonkeyPatch, byte: int
) -> None:
    for separator in (b"", b"\x00"):
        expected = b"a" if byte in _RFC3629 else b"a" + bytes([byte])
        assert _failed_read(monkeypatch, b"a" + bytes([byte]) + separator) == (2, expected)


_NEVER = [b"\xe0\xc0", b"\xed\xa0\x00", b"\xf4\xa0", b"\xf0\xa0\xc0", b"\xf4\xff", b"\xe1\x00\xc0"]


@pytest.mark.parametrize("tail", [*_NEVER, b"\xc2\xf5"])
def test_a_read_failure_keeps_bytes_that_can_never_complete(
    monkeypatch: pytest.MonkeyPatch, tail: bytes
) -> None:
    assert _failed_read(monkeypatch, b"a" + tail) == (2, b"a" + tail.replace(b"\x00", b""))


@pytest.mark.parametrize("byte", [0xC0, 0xC1, 0xC2, 0xE0, 0xF0, 0xF4, 0xF5, 0xFF])
def test_a_live_stream_emits_a_byte_that_cannot_start_a_character(byte: int) -> None:
    data = b"a" + bytes([byte])
    pieces = _cli._strip(iter([data.decode("utf-8", ERRORS)]), "\t\n\r", True, False, "utf-8")
    assert next(pieces).encode("utf-8", ERRORS) == (b"a" if byte in _RFC3629 else data)
