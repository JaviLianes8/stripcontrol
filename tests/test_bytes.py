"""strip_control_bytes: UTF-8 C1 (two bytes) against 8-bit C1 (one byte)."""

from __future__ import annotations

import pytest

from stripcontrol import strip_control_bytes
from stripcontrol._bytes import Encoding, unjoin


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


@pytest.mark.parametrize(
    ("data", "clean"),
    [
        (b"\xef\xbb\x00\xbf", b"\xef"),  # would join into U+FEFF
        (b"\xc2\x1b[31m\xad", b"\xc2"),  # U+00AD
        (b"\xef\xbf\x07\xb9", b"\xef"),  # U+FFF9
        (b"\xe0\xa3\x01\xa2", b"\xe0"),  # U+08E2
        (b"\xc3\x00\xa9", b"\xc3"),  # even a harmless join is refused
        (b"\xf0\xa0\x00\xa0\xa0", b"\xf0"),  # four-byte U+20820
        (b"\xef\xbb\x00\xef\xbb\x00\xbf\xbf", b"\xef\xbb\xef\xbf"),  # nested
    ],
)
def test_removal_never_joins_invalid_bytes_into_a_character(data: bytes, clean: bytes) -> None:
    assert strip_control_bytes(data, format_chars=True) == clean


def test_invalid_bytes_that_were_already_together_stay() -> None:
    assert strip_control_bytes(b"\xe2\xa2A\xf0\xa0\xa0") == b"\xe2\xa2A\xf0\xa0\xa0"


def test_unjoin_holds_back_a_lead_byte_waiting_for_more() -> None:
    lead, cont = "\udcef", "\udcbb"
    assert unjoin("a" + lead + cont, final=False) == ("a", lead + cont)
    assert unjoin(lead + cont + "\udcbf", final=False) == ("", lead)
    assert unjoin("a" + lead + cont) == ("a" + lead + cont, "")
    assert unjoin(lead + "x" + cont, final=False) == (lead + "x" + cont, "")


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
