# stripcontrol

Remove or detect control characters and terminal escape sequences in text, logs and
streams. Typed, zero dependencies, linear time on hostile input.

## Install

```
pip install stripcontrol
```

## Usage

```python
from stripcontrol import strip_control

# A request line written to a log by a server that trusts its input.
line = "GET /\x1b]2;owned\x07 HTTP/1.1\tfrom \x1b[31mred\x1b[0m\x00\n"
print(repr(strip_control(line)))
# 'GET / HTTP/1.1\tfrom red\n'
print(repr(strip_control(line, keep="")))
# 'GET / HTTP/1.1from red'
print(repr(strip_control(line, sequences=False)))
# 'GET /]2;owned HTTP/1.1\tfrom [31mred[0m\n'
```

By default a whole escape sequence goes, not just its first character, so the window
title change above leaves no `]2;owned` behind. Tab, newline and carriage return survive
unless `keep` says otherwise; `sequences=False` removes only the control characters.

Detect, locate or reveal controls instead of removing them:

```python
from stripcontrol import escape_control, find_control, has_control

text = "user=\x1b[2Jadmin\x9b"
print(has_control(text))
# True
print(find_control(text))
# [(5, 27), (14, 155)]
print(escape_control(text))
# user=\x1b[2Jadmin\x9b
```

Unicode format characters (category Cf), such as the bidi overrides behind Trojan Source
(CVE-2021-42574), are included on request:

```python
from stripcontrol import has_control, strip_control

# Shown as "invoiceexe.pdf" by anything that applies the right-to-left override.
name = "invoice" + chr(0x202E) + "fdp.exe"
print(has_control(name))
# False
print(has_control(name, format_chars=True))
# True
print(strip_control(name, format_chars=True))
# invoicefdp.exe
```

Streams and bytes:

```python
from stripcontrol import ControlStripper, strip_control_bytes

stripper = ControlStripper()
chunks = ["progress \x1b[3", "2m42%\x1b[0", "m done\n"]
print(repr("".join(stripper.feed(chunk) for chunk in chunks) + stripper.close()))
# 'progress 42% done\n'

print(strip_control_bytes("Λ\x1b[1m".encode()))
# b'\xce\x9b'
print(strip_control_bytes(b"a\x9b1mb", encoding="latin-1"))
# b'ab'
```

From the shell:

```
stripcontrol access.log > clean.log          # strip files or stdin
tail -f app.log | stripcontrol               # streams, sequences split across reads
stripcontrol --check access.log              # FILE:LINE:COLUMN of each control, exit 1
stripcontrol --escape access.log             # show \x1b instead of acting on it
```

Options: `--chars-only`, `--format-chars`, `--strip-whitespace`, `--latin-1`.
`python -m stripcontrol` works the same.

## API

| Name | What it does |
| --- | --- |
| `strip_control(text, *, keep, sequences, format_chars)` | Text without controls and sequences |
| `strip_control_bytes(data, *, keep, sequences, format_chars, encoding)` | The same for UTF-8 or 8-bit bytes |
| `ControlStripper(*, keep, sequences, format_chars)` | `feed(chunk)`, `close()`, `in_sequence` for streams |
| `has_control(text, *, keep, format_chars)` | Whether any control outside `keep` is present |
| `find_control(text, *, keep, format_chars)` | `(index, codepoint)` of each one |
| `escape_control(text, *, keep, format_chars)` | Controls written as `\xNN`, `\uNNNN` or `\UNNNNNNNN` |
| `STANDARD_WHITESPACE` | `"\t\n\r"`, the default `keep` |
| `UNICODE_VERSION` | The Unicode version of the format character table |

`keep` is a string of characters to leave alone. Non-text arguments raise `TypeError`;
an unknown `encoding` raises `ValueError`.

## What is removed

- **Control characters**: C0 (U+0000 to U+001F), DEL (U+007F) and C1 (U+0080 to U+009F),
  which is exactly the Unicode `Cc` category. With `format_chars=True`, also `Cf` (170
  code points in Unicode 18.0, from a table generated from the Unicode data files, so the
  result does not depend on the Python version).
- **Sequences** (ECMA-48), in 7-bit and 8-bit form: escape sequences (`ESC`, intermediates,
  final), control sequences (`ESC [` or U+009B, parameters, intermediates, final byte),
  OSC strings (`ESC ]` or U+009D, ended by ST or BEL) and DCS, SOS, PM and APC strings
  (ended by ST, which is `ESC \` or U+009C).

A sequence is read the way a terminal reads it (after the DEC parser described at
vt100.net): ESC, CAN, SUB and any C1 control cancel a sequence in progress; C0 controls
inside an escape or control sequence take effect at once (a kept newline survives) and
inside a string they belong to it; DEL inside a sequence is ignored. Where a terminal and a
log reader want different things, this library chooses the reader:

- A line feed ends any sequence, so an unterminated `ESC ]` cannot hide the lines after it.
- A non-ASCII character inside an escape or control sequence ends it and stays as text.
- A sequence still open at the end of the input is dropped, as a terminal would swallow it.
- A sequence whose introducer is in `keep` stays as text (`keep="\x1b"` keeps colours).

Whatever the input, the output holds no control character outside `keep`.

For bytes, `encoding="utf-8"` (the default) reads a C1 control as the two bytes `C2 80` to
`C2 9F` and leaves bytes `80` to `9F` inside valid characters alone (`Λ` is `CE 9B`). A
stray byte `80` to `9F` is removed, because a terminal in 8-bit mode would act on it;
other invalid bytes pass through. `encoding="latin-1"` reads every byte `80` to `9F` as C1.

`format_chars=True` removes zero width joiners and tag characters, which breaks emoji
sequences built from them. `escape_control` is for display: backslashes already in the
text are not escaped, so use `repr` when the result must round-trip.

## Why

Logs, filenames, chat messages and command output carry text from people you do not trust.
Printed to a terminal, an escape sequence in that text can retitle the window, hide lines,
rewrite what is on screen or, in older terminals, type a reply back to the shell: nginx
(CVE-2009-4487), WEBrick (CVE-2009-4492) and kubectl (CVE-2021-25743) all shipped that
bug. Removing only the control characters leaves the sequence bodies behind as noise
(`[31m`, `]0;title`), dropping bytes `80` to `9F` corrupts UTF-8, and a filter applied
chunk by chunk misses sequences split across reads. This library handles those cases in one
small, typed function with nothing else to install.

## Development

`python scripts/fetch_upstream.py` fetches the pinned Unicode and xterm files that some
tests read (they skip without them); `python scripts/gen_format_table.py` regenerates the
format character table. `scripts/check.ps1` runs the whole gate.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
