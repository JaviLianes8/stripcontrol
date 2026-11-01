# stripcontrol 1.0.0 certification report

Date: 2026-11-01. Preparation resumed from d70db60; main is aacacb6.
PyPI has only 0.2.0. Its downloaded wheel has SHA-256
`70e29596b52985a7e8c173ebb1fa7a721e5b6ada0063f8ad6507523c49184a56`.
Every package file matches main after newline normalization.

Progress:
- [x] Resume the existing release branch without discarding commits
- [x] Baseline: format, lint, strict types clean; 164 passed, 11 optional skips
- [x] API review, errors, typing, runnable docstrings (items 1 to 5)
- [x] Ground truth fetched live and independently checked (item 7)
- [x] Contract tests and seeded properties (items 6, 9)
- [x] README, GUIDE, dated CHANGELOG and release metadata (items 11 to 13)
- [x] Built wheel, sdist inspection, upgrade, Python matrix (items 8, 10, 14)
- [x] Final separate gates (item 15)
- [x] Mutation round and table (item 18): 29 of 29 caught
- [ ] PR and guard
- [ ] Independent reviewer (item 16, pending)
- [ ] Merge and publication (item 17, pending)
- [ ] Five independent QA lenses (item 19, pending)

## Scorecard

| Item | Result and evidence |
| --- | --- |
| 1 | PASS: eight stable exports, signatures/defaults pinned, changes in CHANGELOG |
| 2 | PASS: exact `__all__` and public namespace; examples import public names |
| 3 | PASS: public doctests and README/GUIDE examples execute |
| 4 | PASS: strict types for src/tests and installed consumer; `py.typed` ships |
| 5 | PASS: documented TypeError/ValueError, bounded diagnostics, no input hooks |
| 6 | PASS: contracts for every public name, stream state, bytes and CLI |
| 7 | PASS: fetched Unicode/xterm/DEC/ECMA sources and running reference output |
| 8 | PASS: wheel in fresh venv, CLI subprocesses, in-place PyPI 0.2.0 upgrade |
| 9 | PASS: seeded properties and hostile input tests described below |
| 10 | PASS: eight available Python builds, including free-threaded 3.14 |
| 11 | PASS: README examples, absolute links, alternatives and strict twine check |
| 12 | PASS: CHANGELOG 1.0.0 dated 2026-11-01 |
| 13 | PASS: 1.0.0, Production/Stable, Python 3.10+, MIT, URLs, no runtime dependencies |
| 14 | PASS: wheel/sdist entries inspected and compared with the source |
| 15 | PASS: four gates exit 0 separately; 267 tests pass with packaging enabled |
| 16 | Pending independent reviewer |
| 17 | Merge and publication pending; PR and guard tracked above |
| 18 | PASS: 29 deliberate mutations caught; table below |
| 19 | Pending five independent QA lenses; no verdicts recorded |

## API and behavior

The same eight names, signatures and defaults as 0.2.0 are retained. New runtime checks
require actual booleans and distinguish wrong encoding types from unsupported strings.
Errors never quote input values. Text and buffer subclasses use stored data. CLI diagnostics
are bounded; closed output pipes close without a device file. All differences appear in
CHANGELOG 1.0.0 and GUIDE. Existing text and byte filtering rules are unchanged.
The unintended `annotations` attribute is removed; the public namespace now matches
`__all__` exactly, with a contract that runs on every supported interpreter.

Every public callable and stream method/property has a runnable docstring; constants have
module examples. Tests execute README and GUIDE examples. `mypy --strict src tests` is
clean. `py.typed` remains present. TypeError and ValueError are the documented API errors.

## Ground truth

Fetched 2026-11-01: Unicode 18.0.0 DerivedGeneralCategory, xterm patch 411, DEC parser
and ECMA-48 fifth edition. Exact URLs, sizes, hashes and redistribution limits are in
`tests/upstream/MANIFEST.json`. Downloads live outside the repository via
`STRIPCONTROL_UPSTREAM`; tests skip cleanly without them and reject changed hashes.
Unicode and xterm hashes match the original 0.2.0 records. No third-party prose is shipped.

The source tests compare the complete Cc/Cf classification with the fetched Unicode data
and test all 16 C1 pairs extracted from xterm. Python's actual `unicodedata` output is
checked for all 1,114,112 code points it knows. Rich 15.0.0 `Text.from_ansi` is run as a
reference for 1,000 seeded well-formed SGR inputs; results agree. Its decoder source was
fetched from https://raw.githubusercontent.com/Textualize/rich/master/rich/ansi.py on
2026-11-01 (SHA-256 4d0ee9764b2ad1bdd73dcc3fb521af2ff42d84fc4d2ca39840898f4185a9ea93).
Rich is only an oracle for the shared SGR subset. Handwritten grammar examples are labelled.

## Test results

267 passed with both wheel and live PyPI upgrade checks enabled on CPython 3.14.6.
265 passed and two opt-in packaging tests skipped in each installed-wheel matrix run. Seeds 117/90210 cover 3,000 character cases;
73/314159 cover 5,000 byte cases; 20261101 covers 400 CLI streams with random read sizes;
808 covers the 1,000 Rich comparisons. Existing stream split tests, nine 1 MiB hostile
shapes and a 4 MiB control string also pass. Every test has a 300-second timeout.

## Packaging and upgrade

The wheel is built from the sdist, installed into a fresh venv, then driven from an empty
working directory using isolated Python, the console executable and `python -m stripcontrol`.
All CLI flags, missing input continuation, check positions and a real closed output pipe
pass. `twine check --strict` passes for both archives. The inspected wheel has 14 entries:
package modules, `py.typed`, console metadata and MIT LICENSE. The sdist has 36 entries:
source, tests, the manifest, two fetch/generation scripts, docs and metadata. No downloaded
reference content, bytecode, scratch files or certification reports are included.

The upgrade test installs `stripcontrol==0.2.0` from PyPI, exercises its API and CLI,
pickles a partly read stream, upgrades the same venv to the built 1.0.0 wheel and repeats
the consumer calls. The old stream pickle resumes correctly. Fixed exception messages,
encoding type errors, boolean checks and byte subclass handling match the CHANGELOG.
`pip check` passes after upgrade. A separate consumer of all public names passes
`mypy --strict --disallow-any-expr` against the installed wheel and runs successfully.

## Python matrix

The suite from the sdist ran against the installed wheel with no source package extracted
and `pythonpath` disabled. Each interpreter also ran both console and module entry points.
Duplicate executable hashes were consolidated; no installed base interpreter was modified.

| Python build | Installed suite | CLI entry points |
| --- | --- | --- |
| 3.14.6 | 265 passed, 2 opt-in skips | PASS |
| 3.13.18 | 265 passed, 2 opt-in skips | PASS |
| 3.12.16 | 265 passed, 2 opt-in skips | PASS |
| 3.11.18 | 265 passed, 2 opt-in skips | PASS |
| 3.10.22 | 265 passed, 2 opt-in skips | PASS |
| 3.14.10 | 265 passed, 2 opt-in skips | PASS |
| 3.14.10t | 265 passed, 2 opt-in skips | PASS |
| 3.11.11 (Blender 4.5.10) | 265 passed, 2 opt-in skips | PASS |

All supported minor versions 3.10 through 3.14 are represented. The launcher also listed
missing executables for 3.10.19, 3.11.5, 3.11.14, 3.11.17, 3.12.12, 3.12.15, 3.13.2,
3.13.16, 3.14.2/3.14.2t and 3.14.8/3.14.8t; these stale registrations could not run.
User-local Python shortcuts also pointed at missing installations. Working executables
were discovered directly, including regular and free-threaded 3.14.10.

## Gates (item 15)

Each command ran separately and exited 0 on the final source: `ruff format --check .`
(33 files), `ruff check .`, `mypy --strict src` (8 files), `mypy --strict src tests`
(25 files), and `pytest` (267 passed). Both packaging switches were enabled and the
fetched sources and Rich were present. Temporary paths were explicitly selected.

## Mutation round (item 18)

29 deliberate changes were applied one at a time to an isolated copy of the final source.
M01 to M28 ran the contract suite; M29 ran the export contracts after the namespace fix.
All used `-x`, bytecode disabled, a 300-second per-test timeout
and a 330-second process limit. Every change caused a test assertion failure (exit 1);
none survived or depended on a collection error. Restoring the source returned the suite
to 265 passed, 2 skipped; the skips are the separately verified wheel/upgrade checks.
The complete wheel/upgrade suite on the unmodified tree passed 267 tests.

| Id | Deliberate change | Module | Result | Contract that caught it |
| --- | --- | --- | --- | --- |
| M01 | disable sequence removal | `_stripper.py` | caught | `tests/test_api_stability.py::test_stream_empty_feeds_rejection_pickle_and_reset[\x1b]` |
| M02 | ignore kept introducers | `_stripper.py` | caught | `tests/test_bytes.py::test_ascii_sequences_go_in_both_encodings` |
| M03 | close leaves sequence open | `_stripper.py` | caught | `tests/test_api_stability.py::test_stream_empty_feeds_rejection_pickle_and_reset[\x1b]` |
| M04 | accept a parameter as a CSI final | `_stripper.py` | caught | `tests/test_sequences.py::test_control_sequences_go_whole[a\x1b[?25lb-ab]` |
| M05 | LF does not cancel CSI | `_stripper.py` | caught | `tests/test_sequences.py::test_a_line_feed_ends_an_unterminated_sequence` |
| M06 | BEL does not end OSC | `_stripper.py` | caught | `tests/test_bytes.py::test_ascii_sequences_go_in_both_encodings` |
| M07 | BEL ends other strings | `_stripper.py` | caught | `tests/test_sequences.py::test_other_control_strings_end_at_st_only[\x1bP]` |
| M08 | drop non-ASCII recovery character | `_stripper.py` | caught | `tests/test_sequences.py::test_non_ascii_text_abandons_an_escape_or_control_sequence` |
| M09 | omit final C1 control | `_control.py` | caught | `tests/test_control.py::test_strip_removes_c1_controls` |
| M10 | always remove format characters | `_control.py` | caught | `tests/test_bytes.py::test_options_are_passed_on` |
| M11 | one-based find indexes | `_control.py` | caught | `tests/test_api_stability.py::test_subclasses_are_read_without_overridable_conversion` |
| M12 | wrong astral escape width | `_control.py` | caught | `tests/test_control.py::test_escape_control_writes_format_characters_by_width` |
| M13 | UTF-8 interpreted as Latin-1 | `_bytes.py` | caught | `tests/test_bytes.py::test_utf8_c1_is_two_bytes` |
| M14 | preserve stray C1 bytes | `_bytes.py` | caught | `tests/test_bytes.py::test_a_stray_c1_byte_is_removed_but_does_not_start_a_sequence` |
| M15 | allow newly joined characters | `_bytes.py` | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xef\xbb\x00\xbf-\xef]` |
| M16 | four-byte join uses two continuations | `_bytes.py` | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xf0\xa0\x00\xa0\xa0-\xf0]` |
| M17 | skip boolean validation | `_control.py` | caught | `tests/test_api_stability.py::test_boolean_options_reject_non_booleans[0-strip_control]` |
| M18 | honor hostile bytes conversion | `_bytes.py` | caught | `tests/test_api_stability.py::test_subclasses_are_read_without_overridable_conversion` |
| M19 | preserve string subclass hooks | `_control.py` | caught | `tests/test_api_stability.py::test_subclasses_are_read_without_overridable_conversion` |
| M20 | echo usage arguments | `_cli_errors.py` | caught | `tests/test_cli_safety.py::test_usage_error_does_not_echo_argument_values` |
| M21 | wrong check codepoint | `_cli.py` | caught | `tests/test_cli.py::test_check_mode_lists_positions_and_fails` |
| M22 | wrong continued column | `_cli.py` | caught | `tests/test_cli.py::test_check_mode_lists_positions_and_fails` |
| M23 | drop decoder tail | `_cli.py` | caught | `tests/test_cli_edges.py::test_an_incomplete_character_at_the_end_is_kept` |
| M24 | omit output flush | `_cli.py` | caught | `tests/test_cli_edges.py::test_every_piece_is_flushed_for_live_streams` |
| M25 | invert CLI sequence option | `_cli.py` | caught | `tests/test_cli.py::test_filter_strips_stdin` |
| M26 | invoke text inspection hook | `_control.py` | caught | `tests/test_type_hooks.py::test_text_operations_reject_type_hooks[strip_control]` |
| M27 | invoke buffer inspection hook | `_bytes.py` | caught | `tests/test_type_hooks.py::test_bytes_reject_type_hooks` |
| M28 | invoke encoding inspection hook | `_bytes.py` | caught | `tests/test_type_hooks.py::test_bytes_reject_type_hooks` |
| M29 | expose the future import marker | `__init__.py` | caught | `tests/test_contract.py::test_public_namespace_contains_only_documented_exports` |

## Tested archive hashes

`stripcontrol-1.0.0-py3-none-any.whl` SHA-256:
`eac999167b8e0b0ef57315e2c450a0c386c78e4e0e87adc65757b5f17e40faa8`.

`stripcontrol-1.0.0.tar.gz` SHA-256:
`45919bf97970e0c02ad28821cad7d93fa44c6cd19387f679c06a5b4d48595b64`.
