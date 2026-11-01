from __future__ import annotations

import pytest

from stripcontrol import (
    STANDARD_WHITESPACE,
    escape_control,
    find_control,
    has_control,
    strip_control,
)


def test_strip_removes_c0_but_keeps_standard_whitespace() -> None:
    assert strip_control("a\x00b\x01c\tx\ny\rz") == "abc\tx\ny\rz"


def test_strip_removes_del() -> None:
    assert strip_control("a\x7fb") == "ab"


def test_strip_removes_c1_controls() -> None:
    assert strip_control("a\x80b\x85c\x9fd", sequences=False) == "abcd"
    # U+009F is APC, so by default it takes the unterminated string after it too.
    assert strip_control("a\x80b\x85c\x9fd") == "abc"


def test_strip_with_custom_keep_set() -> None:
    assert strip_control("a\x1bb\tc", keep="\x1b") == "a\x1bbc"


def test_strip_with_empty_keep_removes_all_whitespace_controls() -> None:
    assert strip_control("a\tb\nc\rd\x0be\x0cf", keep="") == "abcdef"


def test_strip_leaves_a_clean_string_unchanged() -> None:
    assert strip_control("plain text 123") == "plain text 123"


def test_strip_keeps_printable_unicode_and_nbsp() -> None:
    assert strip_control("café ñ 日本 € \xa0\U0001f600") == "café ñ 日本 € \xa0\U0001f600"


def test_strip_of_empty_string_is_empty() -> None:
    assert strip_control("") == ""


def test_format_characters_stay_unless_asked() -> None:
    text = "a\u202eb\u200bc\ufeffd\xade\U000e0041f"
    assert strip_control(text) == text
    assert strip_control(text, format_chars=True) == "abcdef"


def test_format_characters_in_keep_survive() -> None:
    assert strip_control("a\u200db\u200bc", format_chars=True, keep="\u200d") == "a\u200dbc"


def test_standard_whitespace_is_tab_newline_return() -> None:
    assert STANDARD_WHITESPACE == "\t\n\r"


def test_has_control_true_for_a_control_character() -> None:
    assert has_control("a\x00b") is True


def test_has_control_true_for_del_and_c1() -> None:
    assert has_control("a\x7f") is True
    assert has_control("a\x85") is True


def test_has_control_false_for_standard_whitespace_only() -> None:
    assert has_control("a\tb\nc\rd") is False


def test_has_control_false_for_clean_and_empty() -> None:
    assert has_control("plain") is False
    assert has_control("") is False


def test_has_control_honours_keep_and_format_chars() -> None:
    assert has_control("a\nb", keep="") is True
    assert has_control("a\x1bb", keep="\x1b") is False
    assert has_control("a\u2066b") is False
    assert has_control("a\u2066b", format_chars=True) is True


def test_find_control_reports_index_and_codepoint() -> None:
    assert find_control("a\x00b\x1f") == [(1, 0x00), (3, 0x1F)]


def test_find_control_skips_standard_whitespace() -> None:
    assert find_control("a\tb\nc\r\x7f") == [(6, 0x7F)]


def test_find_control_on_clean_string_is_empty() -> None:
    assert find_control("clean") == []


def test_find_control_honours_keep_and_format_chars() -> None:
    assert find_control("a\tb", keep="") == [(1, 9)]
    assert find_control("\u202ea\x1b", format_chars=True) == [(0, 0x202E), (2, 0x1B)]


def test_escape_control_writes_controls_as_escapes() -> None:
    assert escape_control("a\x1b[31mb\x9b\tc\n") == "a\\x1b[31mb\\x9b\tc\n"


def test_escape_control_honours_keep() -> None:
    assert escape_control("a\tb", keep="") == "a\\x09b"
    assert escape_control("a\x07b", keep="\x07") == "a\x07b"


def test_escape_control_writes_format_characters_by_width() -> None:
    text = "\xad\u202e\U000e0041"
    assert escape_control(text) == text
    assert escape_control(text, format_chars=True) == "\\xad\\u202e\\U000e0041"


@pytest.mark.parametrize("function", [strip_control, has_control, find_control, escape_control])
def test_text_must_be_str(function: object) -> None:
    with pytest.raises(TypeError, match="text must be str"):
        function(b"abc")  # type: ignore[operator]


@pytest.mark.parametrize("function", [strip_control, has_control, find_control, escape_control])
def test_keep_must_be_str(function: object) -> None:
    with pytest.raises(TypeError, match="keep must be str"):
        function("abc", keep=["\n"])  # type: ignore[operator]
