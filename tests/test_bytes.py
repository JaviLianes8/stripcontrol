"""strip_control_bytes: UTF-8 C1 (two bytes) against 8-bit C1 (one byte)."""

from __future__ import annotations

import pytest

from stripcontrol import strip_control_bytes
from stripcontrol._bytes import Encoding


def test_utf8_c1_is_two_bytes() -> None:
    assert strip_control_bytes(b"a\xc2\x85b") == b"ab"
    assert strip_control_bytes(b"a\xc2\x9b31mb") == b"ab"


def test_utf8_continuation_bytes_in_the_c1_range_are_text() -> None:
    # "Λ" is CE 9B, "ś" is C5 9B, U+203A is E2 80 BA: none of them is a control.
    text = "Λś\u203a€".encode()
    assert strip_control_bytes(text) == text


def test_a_stray_c1_byte_is_removed_but_does_not_start_a_sequence() -> None:
    assert strip_control_bytes(b"a\x9b31mb") == b"a31mb"
    assert strip_control_bytes(b"a\x85b") == b"ab"


def test_other_invalid_bytes_pass_through() -> None:
    assert strip_control_bytes(b"a\xff\xc3b\xe2\xa2") == b"a\xff\xc3b\xe2\xa2"
    # A truncated character loses only its bytes in the C1 range.
    assert strip_control_bytes(b"a\xe2\x82") == b"a\xe2"


def test_latin_1_reads_every_byte_80_to_9f_as_c1() -> None:
    assert strip_control_bytes(b"a\x9b31mb", encoding="latin-1") == b"ab"
    assert strip_control_bytes(b"\xce\x9b1m", encoding="latin-1") == b"\xce"
    assert strip_control_bytes(b"caf\xe9\x85", encoding="latin-1") == b"caf\xe9"


def test_ascii_sequences_go_in_both_encodings() -> None:
    encodings: tuple[Encoding, ...] = ("utf-8", "latin-1")
    for encoding in encodings:
        line = b"GET /\x1b]2;owned\x07 HTTP/1.1\n"
        assert strip_control_bytes(line, encoding=encoding) == b"GET / HTTP/1.1\n"


def test_options_are_passed_on() -> None:
    data = "a\tb\u202ec\x1b[1m".encode()
    assert strip_control_bytes(data, keep="") == "ab\u202ec".encode()
    assert strip_control_bytes(data, format_chars=True) == b"a\tbc"
    assert strip_control_bytes(data, sequences=False) == "a\tb\u202ec[1m".encode()


def test_bytearray_and_memoryview_are_accepted() -> None:
    assert strip_control_bytes(bytearray(b"a\x00b")) == b"ab"
    assert strip_control_bytes(memoryview(b"a\x00b")) == b"ab"


def test_text_is_rejected() -> None:
    with pytest.raises(TypeError, match="data must be bytes, not str"):
        strip_control_bytes("abc")  # type: ignore[arg-type]


def test_keep_must_be_text() -> None:
    with pytest.raises(TypeError, match="keep must be str, not bytes"):
        strip_control_bytes(b"abc", keep=b"\n")  # type: ignore[arg-type]


def test_unknown_encoding_is_rejected() -> None:
    with pytest.raises(ValueError, match="encoding must be 'utf-8' or 'latin-1', not 'cp1252'"):
        strip_control_bytes(b"abc", encoding="cp1252")  # type: ignore[arg-type]
