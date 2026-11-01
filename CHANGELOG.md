# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The eight public names, keyword-only options and defaults are stable: text and byte
  stripping, character detection and escaping, incremental streams, whitespace and Unicode
  version constants. Unicode 18.0 format classification matches 0.2.0.
- Python 3.10 through 3.14, typed public API, zero runtime dependencies, CLI and module entry.
- Runnable API and guide examples, contract tests, seeded properties, built-wheel checks
  and in-place upgrade coverage from the actual PyPI 0.2.0 release.

### Changed

- Remove the unintended `annotations` attribute from the package namespace; `__all__`
  retains the same eight names.
- `sequences` and `format_chars` require actual booleans. Previously arbitrary truthy or
  falsey objects were accepted. Invalid values now raise `TypeError`, including empty input.
- Type and encoding errors use fixed messages without input values or type names.
  Validation does not invoke input inspection hooks such as a custom `__class__`.
  A non-string encoding now raises `TypeError`; an unsupported string still raises
  `ValueError`. A released memoryview raises `ValueError` as before.
- String subclasses are read as their underlying text and bytes/bytearray subclasses as
  their stored contents, ignoring conversion, iteration, slicing and buffer hooks.
  Memoryviews keep their raw bytes in logical order, including strided and wide-item views.
- `ControlStripper` identifies its public module as `stripcontrol` for new pickles; old
  pickles referring to `stripcontrol._stripper` remain readable.
- CLI usage errors give a fixed diagnostic instead of echoing arguments. Input errors
  report the error number instead of an arbitrary OS error payload. File labels are escaped
  and limited to 120 characters plus an ellipsis. Closed output pipes close the stream
  quietly without opening a device file; exit codes are unchanged.
- The release helper checks whether the target version exists, allowing upgrades to an
  existing project. It refuses dirty builds, uses a fresh output folder, and stops on
  build or archive validation errors.

### Fixed

- String terminators are consumed even when listed in `keep`, including U+009C and
  ESC-backslash across stream chunks. An ESC inside a string is held for the next character;
  closing an unfinished string discards that pending ESC. Other ESC cancellation rules stay
  unchanged. This applies to text and both byte encodings.
- The upstream fixture fetcher decodes Brotli, gzip and deflate HTTP content before checking
  manifest hashes and saving files. Brotli is a development dependency only.

### Clarified

- Read failures preserve emitted CLI output and discard buffered decoder/joining tails and
  unfinished sequences. Normal EOF finalizes buffered bytes. Later files still run.
- Contracts now pin every stream option across repeated close/reuse, the bare ESC final-byte
  boundary, exact encoding names, and UTF-8 check reports with non-ASCII filenames.
- Fixture-fetch contracts pin case-insensitive HTTP content encodings, including stacks.
  `identity` remains a no-op anywhere in a stack; unsupported encodings raise `ValueError`
  without saving a fixture, even when the decoded bytes would match the manifest.
- Fixture-fetch contracts also pin spaces and horizontal tabs around encoding tokens,
  including before commas, and repeated compression layers in their declared order.
  Manifest validation and storage use the fully decoded content.

## [0.2.0]

### Added

- Whole ECMA-48 sequences are removed with their introducer: escape sequences, CSI
  control sequences and OSC, DCS, SOS, PM and APC control strings, in 7-bit and 8-bit
  form, ended by ST or (for OSC) BEL and cancelled by CAN, SUB, ESC, any C1 control or
  a line feed (so an unterminated sequence never hides the lines after it).
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
