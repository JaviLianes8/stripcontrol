"""ControlStripper: chunk boundaries, invariants on random input, linear time."""

from __future__ import annotations

import itertools
import random
import time

import pytest

from stripcontrol import ControlStripper, has_control, strip_control

# Characters that matter to the parser, weighted towards sequence syntax.
_ALPHABET = [
    *"ab;[]PX^_\\(#m0? é\t\n\r",
    "\x1b",
    "\x07",
    "\x18",
    "\x1a",
    "\x7f",
    "\x00",
    "\x9b",
    "\x9c",
    "\x9d",
    "\x90",
    "\x85",
    "\u202e",
]


def _corpus(seed: int, count: int = 300, length: int = 40) -> list[str]:
    rng = random.Random(seed)
    return ["".join(rng.choices(_ALPHABET, k=rng.randint(0, length))) for _ in range(count)]


def _feed_in_pieces(text: str, cuts: list[int], **options: object) -> str:
    stripper = ControlStripper(**options)  # type: ignore[arg-type]
    bounds = [0, *sorted(cuts), len(text)]
    out = [stripper.feed(text[start:stop]) for start, stop in itertools.pairwise(bounds)]
    return "".join(out) + stripper.close()


def test_every_split_gives_the_one_shot_result() -> None:
    for text in _corpus(1, count=120, length=14):
        expected = strip_control(text)
        for cut in range(len(text) + 1):
            assert _feed_in_pieces(text, [cut]) == expected, (text, cut)
        assert _feed_in_pieces(text, list(range(len(text)))) == expected, text


@pytest.mark.parametrize(
    "options",
    [{}, {"keep": ""}, {"keep": "\x1b\x07"}, {"sequences": False}, {"format_chars": True}],
)
def test_random_splits_match_one_shot_for_every_option(options: dict[str, object]) -> None:
    rng = random.Random(2)
    for text in _corpus(3):
        cuts = [rng.randint(0, len(text)) for _ in range(rng.randint(0, 5))]
        expected = strip_control(text, **options)  # type: ignore[arg-type]
        assert _feed_in_pieces(text, cuts, **options) == expected, (text, cuts)


@pytest.mark.parametrize("keep", ["", "\t\n\r", "\x07\n"])
def test_output_never_holds_a_control_outside_keep(keep: str) -> None:
    for text in _corpus(4):
        clean = strip_control(text, keep=keep, format_chars=True)
        assert not has_control(clean, keep=keep, format_chars=True), (text, clean)
        assert strip_control(text, keep=keep, sequences=False) == "".join(
            char for char in text if char in keep or not has_control(char, keep="")
        )


def test_stripping_is_idempotent() -> None:
    for text in _corpus(5):
        once = strip_control(text)
        assert strip_control(once) == once


def test_printable_text_is_never_dropped_outside_sequences() -> None:
    text = "plain words, digits 0123 and symbols !?[]\\;"
    for prefix in ["", "\x07", "\x00\x85", "\x1b[1m"]:
        assert strip_control(prefix + text) == text


def test_in_sequence_reports_an_open_sequence() -> None:
    stripper = ControlStripper()
    assert stripper.feed("a\x1b]0;ti") == "a"
    assert stripper.in_sequence
    assert stripper.feed("tle\x07b") == "b"
    assert not stripper.in_sequence


def test_close_drops_the_open_sequence_and_resets() -> None:
    stripper = ControlStripper()
    assert stripper.feed("a\x1b[1") == "a"
    assert stripper.close() == ""
    assert not stripper.in_sequence
    assert stripper.feed("2mb") == "2mb"


def test_feed_rejects_bytes() -> None:
    with pytest.raises(TypeError, match="text must be str, not bytes"):
        ControlStripper().feed(b"a")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "unit",
    [
        "\x1b]",  # unterminated OSC openers, each cancelling the last
        "\x9d0;",  # 8-bit OSC openers
        "\x1b[1;",  # CSI without a final
        "\x1b",  # bare ESC run
        "\x9b",  # bare 8-bit CSI run
        "\x1b(",  # escape with intermediates
        "\x00\x85\x7f",  # plain controls
        "\x1bPq" + "#" * 50,  # long DCS payloads
        "a\x1b[",  # text and openers alternating
    ],
)
def test_hostile_input_is_linear(unit: str) -> None:
    size = 1 << 20
    text = unit * (size // len(unit))
    start = time.perf_counter()
    strip_control(text)
    elapsed = time.perf_counter() - start
    # A quadratic scan of 1 MB takes hours; linear work takes well under a second.
    assert elapsed < 10, elapsed


def test_a_long_string_payload_is_skipped_in_one_step() -> None:
    text = "a\x1b]0;" + "x" * (1 << 22) + "\x07b"
    start = time.perf_counter()
    assert strip_control(text) == "ab"
    assert time.perf_counter() - start < 2
