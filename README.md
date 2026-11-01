# stripcontrol

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

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

Unicode format characters (category Cf), including bidi overrides, are included on request:

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

Options: `--chars-only` (strip mode only), `--format-chars`, `--strip-whitespace`,
`--latin-1`. Exit codes: 0 done, 1 `--check` found something, 2 bad usage or an input
that could not be read (the other inputs still run). With `--escape` a stray byte `9B`
and the character U+009B both show as `\x9b`. `python -m stripcontrol` works the same.

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
an unknown string `encoding` raises `ValueError`. Boolean options require `bool`.

## Rules and limits

Controls are Unicode `Cc`: C0, DEL and C1. `format_chars=True` also removes the 170
`Cf` code points in the pinned Unicode 18.0 table, including joiners used in emoji.
The [GUIDE](https://github.com/JaviLianes8/stripcontrol/blob/main/GUIDE.md) describes
sequence recovery, byte encodings, stream reuse, errors and the upgrade from 0.2.0.
The [CHANGELOG](https://github.com/JaviLianes8/stripcontrol/blob/main/CHANGELOG.md)
lists release changes.

This is a log filter, not a terminal emulator or a universal text security policy.
It preserves carriage returns by default, does not undo cursor movements, and leaves
Unicode line separators and ordinary backslashes alone. Use `keep=""` to remove all
controls, or `escape_control` to retain visible evidence. A retained sequence introducer
can still activate terminal behavior. Each CLI file starts a fresh parser.

## Why

Logs and command output can contain terminal instructions from untrusted input. Removing
only ESC leaves bodies such as `[31m` behind; dropping bytes `80` to `9F` corrupts UTF-8;
filtering independent chunks loses sequences split across reads.

For simple character filtering, Python's
[`unicodedata.category`](https://docs.python.org/3/library/unicodedata.html#unicodedata.category)
plus a comprehension is sufficient. It uses the Unicode database bundled with the
interpreter; stripcontrol uses a pinned table and also understands sequence boundaries.
If your application already renders styled text with Rich,
[`Text.from_ansi`](https://rich.readthedocs.io/en/stable/reference/text.html#rich.text.Text.from_ansi)
is useful for decoding ANSI styles. stripcontrol instead provides plain text removal,
byte filtering and incremental parsing without runtime dependencies. The shared SGR
subset is compared with Rich's real output in the tests.

## Development

`python scripts/fetch_upstream.py` fetches the pinned Unicode and xterm files that some
tests read (they skip without them); `python scripts/gen_format_table.py` regenerates the
format character table. `scripts/check.ps1` runs the whole gate.
HTTP content is decoded before hash validation; install the development dependencies
(`pip install -r requirements-dev.txt`) for Brotli support in the fetcher. Set
`STRIPCONTROL_UPSTREAM` to choose a local download folder. Set `STRIPCONTROL_E2E=1` for wheel and CLI checks and
`STRIPCONTROL_E2E_PYPI=1` to also exercise the upgrade from PyPI 0.2.0.
Tests require `pytest-timeout` and use a 300-second per-test limit. Pass
`pytest --basetemp <scratch-folder>` to control temporary test files.

## License

MIT. See [LICENSE](https://github.com/JaviLianes8/stripcontrol/blob/main/LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
