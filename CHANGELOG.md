# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

### Added

- Whole ECMA-48 sequences are removed with their introducer: escape sequences, CSI
  control sequences and OSC, DCS, SOS, PM and APC control strings, in 7-bit and 8-bit
  form, ended by ST or (for OSC) BEL and cancelled by CAN, SUB, ESC or any C1 control.
  `sequences=False` keeps the per-character behaviour.
- `ControlStripper` strips a stream chunk by chunk with the same result as one call.
- `strip_control_bytes` for UTF-8 (C1 as `C2 80..C2 9F`, stray bytes `80..9F` removed)
  and 8-bit (`encoding="latin-1"`) input.
- `format_chars=True` on every function also acts on Unicode format characters (Cf),
  from a table generated from Unicode 18.0 (`UNICODE_VERSION`).
- `escape_control` writes controls as visible escapes.
- `keep` and `format_chars` on `has_control` and `find_control`.
- The `stripcontrol` command line (and `python -m stripcontrol`): filter files or stdin,
  `--check`, `--escape`, `--chars-only`, `--format-chars`, `--strip-whitespace`,
  `--latin-1`.

### Changed

- `strip_control` now removes the body of an escape sequence too:
  `"a\x1b[31mb"` gives `"ab"`, not `"a[31mb"`.
- Non-text arguments raise `TypeError` with a clear message.

## [0.1.0]

- `strip_control` removes C0, DEL and C1 control characters while keeping tab,
  newline and carriage return, with a configurable keep set.
- `has_control` reports whether text holds a control character other than standard
  whitespace.
- `find_control` lists the index and codepoint of each such control character.
