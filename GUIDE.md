# stripcontrol guide

Python 3.10 or later. Import the public API from `stripcontrol`; underscore modules are
implementation details. Defaults are `keep="\t\n\r"`, `sequences=True`,
`format_chars=False`, and `encoding="utf-8"` for bytes.

## Character operations

`has_control`, `find_control` and `escape_control` work on individual characters, never
whole sequences. Indexes from `find_control` count Python string code points, starting at
zero, not bytes or terminal display columns. They include astral characters and lone
surrogates in that count. `escape_control` uses lowercase hex with two, four or eight
digits, respectively `\x`, `\u`, `\U`. Existing backslashes remain unchanged.

```python
from stripcontrol import escape_control, find_control, has_control

text = "\U0001f600\x1b[31m\u202e"
assert find_control(text, format_chars=True) == [(1, 27), (6, 8238)]
assert has_control(text)
assert escape_control("\x07\u202e", format_chars=True) == "\\x07\\u202e"
```

Control characters are exactly Unicode category `Cc`: U+0000..U+001F and
U+007F..U+009F. With `format_chars=True`, the pinned Unicode 18.0.0 `Cf` table also
applies, independently of Python's Unicode version. This includes zero width joiners
and tag characters used in emoji. Surrogates, noncharacters, combining marks, nonbreaking
spaces, and U+2028/U+2029 are otherwise preserved. `keep` only exempts characters that
would have been removed; it does not allow or deny ordinary text.

## Sequence removal

`strip_control` and `ControlStripper` remove escape sequences, CSI control sequences,
and OSC, DCS, SOS, PM and APC strings, with 7-bit and 8-bit introducers. ST is either
ESC followed by backslash or U+009C. BEL also terminates OSC, but not other strings.
Parameters and intermediate bytes are discarded. This filter intentionally tolerates
malformed parameter ordering; it does not validate terminal commands or emulate a screen.

ESC, CAN, SUB and C1 controls cancel the current sequence and are reprocessed as input.
Inside escape/CSI sequences, ordinary C0 controls are removed or kept according to `keep`
without ending the sequence; DEL is ignored. Inside a string they are payload.
These recovery rules have two additional log-oriented choices:

- LF always cancels a sequence and is then kept or removed according to `keep`.
- Non-ASCII text ends escape/CSI sequences and is preserved; inside a string it is payload.

A sequence still open at end of input is discarded. An introducer listed in `keep`
does not open a sequence. String terminators still terminate even if listed in `keep`:
keeping BEL does not preserve the BEL that closes an OSC.

```python
from stripcontrol import strip_control

assert strip_control("a\x1b]2;title\nnext") == "a\nnext"
assert strip_control("a\x1b[31mb", sequences=False) == "a[31mb"
assert strip_control("a\x1b[31mb", keep="\x1b") == "a\x1b[31mb"
```

The grammar comes from [ECMA-48, sections 5.3 to 5.6](https://ecma-international.org/wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf),
recovery is informed by the [DEC parser](https://vt100.net/emu/dec_ansi_parser), and
OSC terminators follow [xterm](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html).
The LF and non-ASCII recovery choices are this library's policy, not claims of terminal
conformance. These sources were fetched on 2026-11-01; hashes are recorded in the
[manifest](https://github.com/JaviLianes8/stripcontrol/blob/main/tests/upstream/MANIFEST.json).

## Streams

`feed` returns available clean text and preserves parser state. Empty feeds do nothing.
`in_sequence` reports whether a sequence is open. `close` always returns `""`, discards
open state and resets the instance for reuse, preserving options. Repeated `close` is safe.
Rejected feed types do not change state. A mutable stream is not thread-safe; use one
instance per input. Memory is proportional to the current chunk, not the total stream.

```python
from stripcontrol import ControlStripper

stream = ControlStripper()
assert stream.feed("ok\x1b[") == "ok" and stream.in_sequence
assert stream.feed("31mred") == "red" and not stream.in_sequence
assert stream.close() == ""
assert stream.feed("new") == "new"
```

## Bytes

`strip_control_bytes` accepts `bytes`, `bytearray` and `memoryview`, returns `bytes`, and
never mutates the input. Views use raw bytes in logical order, regardless of item format.
`utf-8` decodes valid characters before filtering, so continuation bytes in the C1 range
inside valid characters survive. Stray bytes `80`..`9F` are removed without opening a
sequence, even if `keep` contains the corresponding Unicode character.

Other invalid bytes are preserved except when removal joins them into a valid UTF-8
character. Then the joining continuation bytes are dropped, retaining the lead byte.
This prevents removal from synthesizing previously unchecked characters. `latin-1`
maps each byte directly to a character, so every byte `80`..`9F` is a C1 control.

```python
from stripcontrol import strip_control_bytes

assert strip_control_bytes(b"\xce\x9b\x9b31m") == b"\xce\x9b31m"
assert strip_control_bytes(b"\x9b31m", encoding="latin-1") == b""
assert strip_control_bytes(b"\xef\xbb\x00\xbf") == b"\xef"
```

## Errors and command line

Wrong `text`, `keep`, `data`, encoding types or non-boolean options raise `TypeError`.
An unsupported encoding string or a released memoryview raises `ValueError`. Other valid
buffers are accepted, including empty and strided views. Error messages do not quote
values. No dedicated exception class is required to distinguish these caller errors.

The CLI reads binary stdin or named files, streams UTF-8 by default, and resets state
between files. `--latin-1`, `--strip-whitespace`, `--format-chars` map to the API options.
`--chars-only` disables sequences and is only valid in strip mode. `--escape` shows
characters and stray C1 bytes as escapes; `--check` reports each detected character
without stripping. Positions are one-based lines and code-point columns; only LF starts
a line. Stray undecodable bytes count as one column. Check reports are UTF-8 in both modes.

Exit codes are 0 for success, 1 for findings under `--check`, 2 for usage/input errors.
Input errors do not stop later files. Closed output pipes end quietly with the status so
far. Other output errors propagate. Diagnostics escape and truncate file labels to 120
characters plus `...`; usage errors do not echo arguments and input errors report errno.

## Upgrade from 0.2.0

All eight names, parameter names, defaults and normal stripping results are preserved.
Boolean options now require `bool`; convert values explicitly if needed. Exception
messages and CLI diagnostics are bounded and must not be parsed as a protocol. String
and byte subclasses use their stored content instead of custom conversion hooks. New
stream pickles refer to the public module; old private-module pickles remain readable.
See the [dated changelog](https://github.com/JaviLianes8/stripcontrol/blob/main/CHANGELOG.md).
