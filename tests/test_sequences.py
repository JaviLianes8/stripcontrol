"""Whole-sequence removal.

The expected values are written by hand from the grammar in ECMA-48 5th edition (5.3
escape sequences, 5.4 control sequences, 5.6 control strings), the recovery rules of the
DEC parser (https://vt100.net/emu/dec_ansi_parser) and the OSC terminators listed in XTerm
Control Sequences (https://invisible-island.net/xterm/ctlseqs/ctlseqs.html).
"""

from __future__ import annotations

import pytest

from stripcontrol import strip_control

ESC, BEL, ST7 = "\x1b", "\x07", "\x1b\\"
CSI8, OSC8, DCS8, SOS8, PM8, APC8, ST8 = "\x9b", "\x9d", "\x90", "\x98", "\x9e", "\x9f", "\x9c"


@pytest.mark.parametrize(
    ("dirty", "clean"),
    [
        ("a\x1b[31mred\x1b[0m", "ared"),  # SGR colour on and off
        ("a\x1b[1;38;2;255;0;0mb", "ab"),  # parameters with sub-fields
        ("a\x1b[?25lb", "ab"),  # private marker
        ("a\x1b[ qb", "ab"),  # intermediate byte 02/00 before the final
        ("a\x1b[2 !pb", "ab"),  # several intermediates
        ("a\x1b[1;2pb", "ab"),  # final in the private range 07/00..07/14
        ("a\x9b31mb", "ab"),  # 8-bit CSI
        ("a\x1b[b", "a"),  # 'b' (06/02) is itself a final byte
    ],
)
def test_control_sequences_go_whole(dirty: str, clean: str) -> None:
    assert strip_control(dirty) == clean


@pytest.mark.parametrize(
    ("dirty", "clean"),
    [
        ("a\x1b(Bb", "ab"),  # nF: designate a character set
        ("a\x1b#8b", "ab"),  # nF with final 03/08
        ("a\x1b7b\x1b8c", "abc"),  # Fp: save and restore cursor
        ("a\x1bcb", "ab"),  # Fs: reset
        ("a\x1bDb", "ab"),  # Fe: IND in 7-bit form
        ("a\x1b  !Fb", "ab"),  # many intermediates
    ],
)
def test_escape_sequences_go_whole(dirty: str, clean: str) -> None:
    assert strip_control(dirty) == clean


@pytest.mark.parametrize("opener", [ESC + "]", OSC8])
@pytest.mark.parametrize("closer", [ST7, ST8, BEL])
def test_osc_strings_end_at_st_or_bel(opener: str, closer: str) -> None:
    assert strip_control(f"a{opener}0;pwned{closer}b") == "ab"


@pytest.mark.parametrize(
    "opener", [ESC + "P", DCS8, ESC + "X", SOS8, ESC + "^", PM8, ESC + "_", APC8]
)
def test_other_control_strings_end_at_st_only(opener: str) -> None:
    assert strip_control(f"a{opener}q#0;1\x07still{ST7}b") == "ab"
    assert strip_control(f"a{opener}payload{ST8}b") == "ab"


def test_osc_8_hyperlink_keeps_only_its_text() -> None:
    link = "\x1b]8;;https://example.test\x1b\\label\x1b]8;;\x1b\\"
    assert strip_control(f"see {link}.") == "see label."


@pytest.mark.parametrize("cancel", ["\x18", "\x1a"])
def test_can_and_sub_cancel_a_sequence(cancel: str) -> None:
    assert strip_control(f"a\x1b[12{cancel}3mb") == "a3mb"
    assert strip_control(f"a\x1b]0;t{cancel}itle") == "aitle"
    assert strip_control(f"a\x1b({cancel}Bb") == "aBb"


def test_escape_cancels_a_sequence_and_starts_another() -> None:
    assert strip_control("a\x1b[12\x1b[3mb") == "ab"
    assert strip_control("a\x1b]0;x\x1b[1mb") == "ab"


@pytest.mark.parametrize("c1", ["\x85", "\x9c", "\x84", "\x9a"])
def test_any_c1_control_cancels_a_sequence(c1: str) -> None:
    assert strip_control(f"a\x1b[12{c1}3mb") == "a3mb"
    assert strip_control(f"a\x1bP1{c1}tail") == "atail"


def test_a_c1_introducer_inside_a_string_starts_a_new_sequence() -> None:
    assert strip_control("a\x9d0;x\x9b1mb") == "ab"


def test_a_line_feed_ends_an_unterminated_sequence() -> None:
    # Own rule: a terminal would keep swallowing; a sanitiser must not hide later lines.
    assert strip_control("a\x1b]0;evil\nnext line") == "a\nnext line"
    assert strip_control("a\x1bP1q\nnext", keep="") == "anext"
    assert strip_control("a\x1b[12\nm") == "a\nm"


def test_c0_controls_inside_a_control_sequence_act_and_the_sequence_goes_on() -> None:
    assert strip_control("a\x1b[1\t2mb") == "a\tb"
    assert strip_control("a\x1b[1\x002mb") == "ab"
    assert strip_control("a\x1b\rDb") == "a\rb"


def test_c0_controls_inside_a_string_are_part_of_it() -> None:
    assert strip_control("a\x1b]0;x\ty\x07b") == "ab"
    assert strip_control("a\x1bPx\ty\x1b\\b") == "ab"


def test_del_inside_a_sequence_is_ignored() -> None:
    assert strip_control("a\x1b[1\x7f2mb") == "ab"
    assert strip_control("a\x1b\x7f(Bb") == "ab"


def test_non_ascii_text_abandons_an_escape_or_control_sequence() -> None:
    assert strip_control("a\x1bé") == "aé"
    assert strip_control("a\x1b[12日本") == "a日本"
    assert strip_control("a\x1b(é") == "aé"


def test_non_ascii_text_inside_a_string_is_payload() -> None:
    assert strip_control("a\x1b]0;título\x07b") == "ab"


def test_unterminated_sequences_run_to_the_end() -> None:
    assert strip_control("a\x1b") == "a"
    assert strip_control("a\x1b[") == "a"
    assert strip_control("a\x1b[1;2") == "a"
    assert strip_control("a\x1b]0;title") == "a"
    assert strip_control("a\x1b(") == "a"


def test_a_kept_introducer_leaves_its_sequence_as_text() -> None:
    assert strip_control("a\x1b[31mb", keep="\x1b") == "a\x1b[31mb"
    assert strip_control("a\x9b31mb", keep="\x9b") == "a\x9b31mb"
    assert strip_control("a\x9d0;t\x1b\\b", keep="\x1b") == "a\x1b\\b"


def test_a_kept_bel_still_ends_an_osc() -> None:
    assert strip_control("a\x1b]0;t\x07b\x07", keep="\x07") == "ab\x07"


def test_chars_only_mode_removes_just_the_controls() -> None:
    assert strip_control("a\x1b[31mb\x9d0;t\x07", sequences=False) == "a[31mb0;t"


@pytest.mark.parametrize(
    "payload",
    [
        # CVE-2009-4487 / CVE-2009-4492: retitle the window of whoever reads the log.
        "GET /\x1b]2;owned\x07 HTTP/1.1",
        # Clear the screen, move home, hide the cursor.
        "GET /\x1b[2J\x1b[H\x1b[?25l HTTP/1.1",
        # Query the title and have it typed back (the classic report attack).
        "GET /\x1b[21t HTTP/1.1",
        # 8-bit forms of the same.
        "GET /\x9d2;owned\x9c\x9b2J HTTP/1.1",
    ],
)
def test_log_injection_payloads_are_neutralised(payload: str) -> None:
    assert strip_control(payload) == "GET / HTTP/1.1"
