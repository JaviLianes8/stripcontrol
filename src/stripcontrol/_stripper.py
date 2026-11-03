"""Remove control characters and whole ECMA-48 sequences, in one call or chunk by chunk."""

from __future__ import annotations

import re

from ._control import STANDARD_WHITESPACE, check_bool, check_text, pattern

# Parser states, after the DEC parser (vt100.net/emu/dec_ansi_parser), reduced to what
# removal needs: every parameter, intermediate and payload character is dropped.
_GROUND, _ESCAPE, _ESCAPE_INTERMEDIATE, _CSI, _OSC, _STRING = range(6)
_STRING_ESCAPE = 6  # A possible ST, including an ESC kept by the caller.

# The 8-bit introducers and the characters that follow ESC in their 7-bit form.
_C1_INTRODUCERS = {
    "\x9b": _CSI,
    "\x9d": _OSC,
    "\x90": _STRING,  # DCS
    "\x98": _STRING,  # SOS
    "\x9e": _STRING,  # PM
    "\x9f": _STRING,  # APC
}
_ESC_INTRODUCERS = {"[": _CSI, "]": _OSC, "P": _STRING, "X": _STRING, "^": _STRING, "_": _STRING}

# Characters that end any sequence in progress, then count as ordinary input: ESC, CAN,
# SUB and every C1 control (as in the DEC parser), and LF, so that an unterminated
# sequence never hides the lines after it.
_CANCEL = "\x0a\x18\x1a\x1b\x80-\x9f"
_OSC_STOP = re.compile(f"[\x07{_CANCEL}]")  # BEL also ends an OSC, as in xterm
_STRING_STOP = re.compile(f"[{_CANCEL}]")
_CSI_BODY_END = re.compile("[^\x20-\x3f]")  # past the parameter and intermediate bytes


def _cancels(code: int) -> bool:
    # C1 controls cancel too: inside a string the stop pattern finds them, and inside an
    # escape or control sequence every character above 0x7F ends it (see feed).
    return code in (0x0A, 0x18, 0x1A, 0x1B)


class ControlStripper:
    r"""Incremental :func:`strip_control`: feed text in chunks, get the clean text back.

    The parser state is kept between calls, so a sequence split across chunks is removed
    exactly as it would be in one call. A sequence still open at the end of the input is
    dropped, as a terminal would swallow it.
    Wrong argument types raise TypeError. A stream is mutable and not thread-safe.

    >>> from stripcontrol import ControlStripper
    >>> stream = ControlStripper()
    >>> stream.feed("a\x1b[3") + stream.feed("1mb") + stream.close()
    'ab'
    """

    def __init__(
        self,
        *,
        keep: str = STANDARD_WHITESPACE,
        sequences: bool = True,
        format_chars: bool = False,
    ) -> None:
        self._keep = frozenset(check_text(keep, "keep"))
        check_bool(sequences, "sequences")
        self._sequences = sequences
        self._special = pattern(format_chars)
        self._state = _GROUND

    @property
    def in_sequence(self) -> bool:
        r"""Whether the input so far ends inside an escape sequence or control string.

        >>> from stripcontrol import ControlStripper
        >>> stream = ControlStripper()
        >>> stream.feed("\x1b["), stream.in_sequence
        ('', True)
        """
        return self._state != _GROUND

    def feed(self, text: str) -> str:
        r"""Return clean text, continuing from the previous chunk; reject non-text.

        >>> from stripcontrol import ControlStripper
        >>> ControlStripper().feed("a\x00b")
        'ab'
        """
        text = check_text(text)
        out: list[str] = []
        state, pos, end = self._state, 0, len(text)
        while pos < end:
            if state == _GROUND:
                match = self._special.search(text, pos)
                if match is None:
                    out.append(text[pos:])
                    break
                start = match.start()
                out.append(text[pos:start])
                char = text[start]
                pos = start + 1
                if char in self._keep:
                    out.append(char)
                elif self._sequences:
                    state = _ESCAPE if char == "\x1b" else _C1_INTRODUCERS.get(char, _GROUND)
                continue
            char = text[pos]
            code = ord(char)
            if state == _STRING_ESCAPE:
                state = _GROUND
                if char == "\\":
                    pos += 1
                elif "\x1b" in self._keep:
                    out.append("\x1b")
                else:
                    state = _ESCAPE
            elif state in (_OSC, _STRING):
                stop = (_OSC_STOP if state == _OSC else _STRING_STOP).search(text, pos)
                if stop is None:
                    pos = end
                elif text[stop.start()] in "\x07\x9c":
                    state, pos = _GROUND, stop.start() + 1
                elif text[stop.start()] == "\x1b":
                    state, pos = _STRING_ESCAPE, stop.start() + 1
                else:
                    state, pos = _GROUND, stop.start()
            elif _cancels(code):
                state = _GROUND  # read the same character again from the ground state
            elif code < 0x20:
                # A C0 control inside an escape or control sequence acts at once.
                if char in self._keep:
                    out.append(char)
                pos += 1
            elif code == 0x7F:
                pos += 1
            elif code > 0x7F:
                # Not part of any 7-bit sequence: the sequence is abandoned, the text stays.
                state = _GROUND
            elif state == _CSI:
                if code >= 0x40:  # the final byte
                    state, pos = _GROUND, pos + 1
                else:
                    body_end = _CSI_BODY_END.search(text, pos)
                    pos = end if body_end is None else body_end.start()
            elif state == _ESCAPE:
                pos += 1
                # An intermediate byte, a final byte, or the end of a 7-bit introducer.
                after = _ESC_INTRODUCERS.get(char, _GROUND)
                state = _ESCAPE_INTERMEDIATE if code < 0x30 else after
            else:
                pos += 1
                if code >= 0x30:
                    state = _GROUND
        self._state = state
        return "".join(out)

    def close(self) -> str:
        """Drop any open sequence, reset for reuse, and return an empty string.

        >>> from stripcontrol import ControlStripper
        >>> stream = ControlStripper()
        >>> stream.close(), stream.in_sequence, stream.feed("new")
        ('', False, 'new')
        """
        self._state = _GROUND
        return ""


def strip_control(
    text: str,
    *,
    keep: str = STANDARD_WHITESPACE,
    sequences: bool = True,
    format_chars: bool = False,
) -> str:
    r"""Return ``text`` without control characters, keeping those in ``keep``.

    Control characters are the C0 range (U+0000..U+001F), DEL (U+007F) and the C1 range
    (U+0080..U+009F). With ``sequences=True`` (the default) whole ECMA-48 sequences go
    with their introducer: escape sequences, CSI control sequences and OSC, DCS, SOS, PM
    and APC control strings, in 7-bit (``ESC [``) and 8-bit (``U+009B``) form. A sequence
    whose introducer is listed in ``keep`` is left as text. ``format_chars=True`` also
    removes Unicode format characters (category Cf), such as bidi overrides.
    Wrong argument types raise TypeError. LF cancels incomplete sequences.

    >>> from stripcontrol import strip_control
    >>> strip_control("a\x1b[31mb\x00\n")
    'ab\n'
    """
    stripper = ControlStripper(keep=keep, sequences=sequences, format_chars=format_chars)
    return stripper.feed(text) + stripper.close()
