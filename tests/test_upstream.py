"""Contracts against the pinned sources in tests/upstream/MANIFEST.json (skipped if absent)."""

from __future__ import annotations

import html
import re
import sys
import unicodedata
from pathlib import Path

import pytest

from stripcontrol import UNICODE_VERSION, _format_table, find_control, strip_control
from stripcontrol._format_table import FORMAT_RANGES

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from gen_format_table import category_ranges, render


def _expand(ranges: list[tuple[int, int]] | tuple[tuple[int, int], ...]) -> set[int]:
    return {code for start, end in ranges for code in range(start, end + 1)}


def test_cc_in_the_ucd_is_exactly_what_counts_as_control(general_category: str) -> None:
    cc = _expand(category_ranges(general_category, "Cc"))
    assert cc == set(range(0x20)) | set(range(0x7F, 0xA0))
    text = "".join(map(chr, sorted(cc)))
    assert [code for _, code in find_control(text, keep="")] == sorted(cc)
    assert strip_control(text, keep="", sequences=False) == ""


def test_the_format_table_is_the_ucd_cf_set(general_category: str) -> None:
    cf = _expand(category_ranges(general_category, "Cf"))
    assert _expand(FORMAT_RANGES) == cf
    assert len(cf) == 170
    found = find_control("".join(map(chr, sorted(cf))), format_chars=True)
    assert [code for _, code in found] == sorted(cf)


def test_the_generated_module_is_up_to_date(general_category: str) -> None:
    module = Path(_format_table.__file__)
    expected = render(category_ranges(general_category, "Cf"), UNICODE_VERSION)
    assert module.read_text(encoding="utf-8") == expected
    assert "18.0.0" in general_category.splitlines()[0]


def test_unicodedata_agrees_on_every_character_it_knows() -> None:
    table = _expand(FORMAT_RANGES)
    for code in range(0x110000):
        category = unicodedata.category(chr(code))
        if category == "Cf":
            assert code in table, hex(code)
        if code in table and category != "Cn":
            assert category == "Cf", hex(code)


def _c1_pairs(page: str) -> list[tuple[str, str]]:
    text = html.unescape(re.sub(r"<[^>]+>", "", page))
    section = text.split("C1 (8-Bit) Control Characters", 1)[1].split("VT100-related", 1)[0]
    return [
        (final, chr(int(code, 16)))
        for final, code in re.findall(r"ESC (\S)\s*\n[^\n]*?is (0x[0-9a-f]{2})", section)
    ]


def test_xterm_lists_the_c1_pairs(xterm_ctlseqs: str) -> None:
    pairs = dict(_c1_pairs(xterm_ctlseqs))
    assert len(pairs) == 16
    assert pairs["["] == "\x9b" and pairs["]"] == "\x9d" and pairs["\\"] == "\x9c"


@pytest.mark.parametrize(
    "tail", ["1;2mtext", "0;title\x07after", "q#1\x1b\\after", "text\x9cafter", "(Bafter"]
)
def test_7_bit_and_8_bit_forms_strip_alike(xterm_ctlseqs: str, tail: str) -> None:
    for final, c1 in _c1_pairs(xterm_ctlseqs):
        seven = strip_control(f"a\x1b{final}{tail}")
        eight = strip_control(f"a{c1}{tail}")
        assert seven == eight, (final, tail)


def test_xterm_accepts_bel_and_st_for_osc(xterm_ctlseqs: str) -> None:
    text = html.unescape(re.sub(r"<[^>]+>", "", xterm_ctlseqs))
    # The two OSC forms in the page's own notation.
    assert re.search(r"OSC Ps ; Pt BEL", text) and re.search(r"OSC Ps ; Pt ST", text)
    assert strip_control("a\x1b]2;t\x07b\x1b]2;t\x1b\\c") == "abc"
