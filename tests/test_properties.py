"""Seeded properties with independent character classification and real reference output."""

from __future__ import annotations

import importlib
import random
import unicodedata

import pytest

from stripcontrol import (
    ControlStripper,
    escape_control,
    find_control,
    has_control,
    strip_control,
    strip_control_bytes,
)


def _special(char: str, formats: bool) -> bool:
    return unicodedata.category(char) in ({"Cc", "Cf"} if formats else {"Cc"})


@pytest.mark.parametrize("seed", [117, 90210])
def test_character_operations_match_unicodedata(seed: int) -> None:
    rng = random.Random(seed)
    alphabet = [*map(chr, range(256)), "\u202e", "\u200d", "\U000e0041", "\ud800", "\U0001f600"]
    for _ in range(1500):
        text = "".join(rng.choices(alphabet, k=rng.randrange(80)))
        keep = "".join(rng.choices(alphabet, k=8))
        formats = rng.choice([False, True])
        hits = [(i, ord(c)) for i, c in enumerate(text) if _special(c, formats) and c not in keep]
        assert find_control(text, keep=keep, format_chars=formats) == hits
        assert has_control(text, keep=keep, format_chars=formats) == bool(hits)
        removed = {index for index, _ in hits}
        expected = "".join(c for i, c in enumerate(text) if i not in removed)
        assert strip_control(text, keep=keep, sequences=False, format_chars=formats) == expected
        # ascii() supplies Python's independently implemented escape representation.
        escaped = "".join(
            (ascii(c)[1:-1] if ord(c) >= 256 else f"\\x{ord(c):02x}") if i in removed else c
            for i, c in enumerate(text)
        )
        assert escape_control(text, keep=keep, format_chars=formats) == escaped


@pytest.mark.parametrize("seed", [73, 314159])
def test_bytes_are_idempotent_and_never_create_decoded_characters(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(2500):
        data = bytes(rng.randrange(256) for _ in range(rng.randrange(120)))
        formats, sequences = rng.choice([False, True]), rng.choice([False, True])
        keep = rng.choice(["", "\t\n\r", "\x1b\x9b\x07"])
        cleaned = strip_control_bytes(data, keep=keep, sequences=sequences, format_chars=formats)
        assert (
            strip_control_bytes(cleaned, keep=keep, sequences=sequences, format_chars=formats)
            == cleaned
        )
        original = data.decode("utf-8", "surrogateescape")
        result = cleaned.decode("utf-8", "surrogateescape")
        assert not has_control(result, keep=keep, format_chars=formats)
        assert all(c in original for c in result)
        latin = strip_control(
            data.decode("latin-1"), keep=keep, sequences=sequences, format_chars=formats
        )
        assert strip_control_bytes(
            data, encoding="latin-1", keep=keep, sequences=sequences, format_chars=formats
        ) == latin.encode("latin-1")


def test_well_formed_sgr_matches_rich_reference_output() -> None:
    # Rich's decoder is a rendering oracle only for this shared, well-formed subset.
    # Source inspected live 2026-11-01: https://github.com/Textualize/rich/blob/master/rich/ansi.py
    pytest.importorskip("rich")
    text_type = importlib.import_module("rich.text").Text
    rng = random.Random(808)
    for _ in range(1000):
        text = "".join(
            f"\x1b[{rng.choice([0, 1, 2, 3, 4, 7, 22, 31, 32, 39, 41, 49])}m"
            + rng.choice(["hello", "world", "\u03bb", " "])
            for _ in range(rng.randrange(1, 20))
        )
        assert strip_control(text) == text_type.from_ansi(text).plain
        stream = ControlStripper()
        assert "".join(stream.feed(c) for c in text) + stream.close() == strip_control(text)
