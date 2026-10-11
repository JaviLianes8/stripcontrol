from stripcontrol import STANDARD_WHITESPACE, find_control, has_control, strip_control


def test_strip_removes_c0_but_keeps_standard_whitespace() -> None:
    assert strip_control("a\x00b\x01c\tx\ny\rz") == "abc\tx\ny\rz"


def test_strip_removes_del() -> None:
    assert strip_control("a\x7fb") == "ab"


def test_strip_removes_c1_controls() -> None:
    assert strip_control("a\x80b\x9fc") == "abc"


def test_strip_with_custom_keep_set() -> None:
    assert strip_control("a\x1bb\tc", keep="\x1b") == "a\x1bbc"


def test_strip_with_empty_keep_removes_all_whitespace_controls() -> None:
    assert strip_control("a\tb\nc", keep="") == "abc"


def test_strip_leaves_a_clean_string_unchanged() -> None:
    assert strip_control("plain text 123") == "plain text 123"


def test_strip_keeps_printable_unicode() -> None:
    assert strip_control("café ñ 日本 €") == "café ñ 日本 €"


def test_strip_of_empty_string_is_empty() -> None:
    assert strip_control("") == ""


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


def test_find_control_reports_index_and_codepoint() -> None:
    assert find_control("a\x00b\x1f") == [(1, 0x00), (3, 0x1F)]


def test_find_control_skips_standard_whitespace() -> None:
    assert find_control("a\tb\nc\r\x7f") == [(6, 0x7F)]


def test_find_control_on_clean_string_is_empty() -> None:
    assert find_control("clean") == []
