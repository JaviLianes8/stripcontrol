# stripcontrol 1.0.0 certification report

Date: 2026-11-01. Preparation resumed from d70db60; main is aacacb6.
Preparation evidence below predates the fixes recorded in the QA rounds at the end.
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
- [x] Mutation round and table (item 18): 29 of 29 caught; review round 1 added 38 byte-boundary mutations; review round 2 added 5 lookahead mutations; review rounds 3 and 4 added 6 more, all caught
- [x] [PR #3](https://github.com/JaviLianes8/stripcontrol/pull/3), `release/1.0.0`; guard CLEAN
- [x] Independent reviewer (item 16): round 5 PASS at 35ba1ba
- [x] Five independent QA lenses (item 19): all five PASS
- [x] Final gates on a fresh clone of `release/1.0.0`
- [ ] Merge and publication by the maintainer (after this report)

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
| 16 | PASS: independent reviewer round 5 at 35ba1ba; rounds 1 to 4 findings fixed below |
| 17 | PASS: PR #3 from `release/1.0.0` to main is open and the trace guard is CLEAN; the maintainer merges and publishes next |
| 18 | PASS: 29 deliberate mutations caught; 37 of 38 byte-boundary mutations caught, one proven equivalent; 5 of 5 lookahead mutations caught; 6 of 6 review round 3 and 4 mutations caught; tables below |
| 19 | PASS: all five QA lenses report PASS; table under Final verdicts |

## API and behavior

The same eight names, signatures and defaults as 0.2.0 are retained. New runtime checks
require actual booleans and distinguish wrong encoding types from unsupported strings.
Errors never quote input values. Text and buffer subclasses use stored data. CLI diagnostics
are bounded; closed output pipes close without a device file. All differences appear in
CHANGELOG 1.0.0 and GUIDE. QA round 1 corrects kept string terminators in text and bytes.
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

### Byte-boundary mutations (review round 1)

Each change was applied alone to `src/stripcontrol/_bytes.py` in a scratch clone of
`9d14bd8`, then the full suite ran with `-x`, bytecode disabled and a 300-second per-test
timeout. Caught means exit 1 through a test failure. The restored clone passes again.

| Id | Deliberate change | Result | First failing contract |
| --- | --- | --- | --- |
| B01 | two-byte leads start at C0 (reviewer R7) | caught | `tests/test_bytes_boundaries.py::test_only_a_lead_byte_is_held_back_at_the_end[c0]` |
| B02 | two-byte leads start at C1 | caught | `tests/test_bytes_boundaries.py::test_only_a_lead_byte_is_held_back_at_the_end[c1]` |
| B03 | two-byte leads start at C3 | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xc2\x1b[31m\xad-\xc2]` |
| B04 | two-byte leads end at DE | caught | `tests/test_bytes_boundaries.py::test_only_a_lead_byte_is_held_back_at_the_end[df]` |
| B05 | two-byte leads end at E0 | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xe0\xa3\x01\xa2-\xe0]` |
| B06 | three-byte leads start at E1 | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xe0\xa3\x01\xa2-\xe0]` |
| B07 | three-byte leads end at EE | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xef\xbb\x00\xbf-\xef]` |
| B08 | three-byte leads end at F0 | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xf0\xa0\x00\xa0\xa0-\xf0]` |
| B09 | four-byte leads start at F1 | caught | `tests/test_bytes.py::test_removal_never_joins_invalid_bytes_into_a_character[\xf0\xa0\x00\xa0\xa0-\xf0]` |
| B10 | four-byte leads end at F3 | caught | `tests/test_bytes_boundaries.py::test_only_a_lead_byte_is_held_back_at_the_end[f4]` |
| B11 | four-byte leads end at F5 | caught | `tests/test_bytes_boundaries.py::test_only_a_lead_byte_is_held_back_at_the_end[f5]` |
| B12 | four-byte leads end at F7 (reviewer variant) | caught | `tests/test_bytes_boundaries.py::test_only_a_lead_byte_is_held_back_at_the_end[f5]` |
| B13 | E0 second byte starts at 9F | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e0]` |
| B14 | E0 second byte starts at A1 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e0]` |
| B15 | E0 second byte ends at BE | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e0]` |
| B16 | E0 second byte ends at C0 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e0]` |
| B17 | ED second byte starts at 81 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[ed]` |
| B18 | ED second byte ends at 9E | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[ed]` |
| B19 | ED second byte ends at A0 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[ed]` |
| B20 | F0 second byte starts at 8F | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f0]` |
| B21 | F0 second byte starts at 91 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f0]` |
| B22 | F0 second byte ends at BE | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f0]` |
| B23 | F0 second byte ends at C0 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f0]` |
| B24 | F4 second byte starts at 81 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f4]` |
| B25 | F4 second byte ends at 8E | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f4]` |
| B26 | F4 second byte ends at 90 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[f4]` |
| B27 | other second bytes starts at 81 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e1]` |
| B28 | other second bytes ends at BE | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e1]` |
| B29 | other second bytes ends at C0 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e1]` |
| B30 | third and fourth bytes starts at 81 | caught | `tests/test_bytes_boundaries.py::test_later_bytes_must_be_continuations_to_be_held[240]` |
| B31 | third and fourth bytes ends at BE | caught | `tests/test_bytes_boundaries.py::test_later_bytes_must_be_continuations_to_be_held[240]` |
| B32 | third and fourth bytes ends at C0 | caught | `tests/test_bytes_boundaries.py::test_later_bytes_must_be_continuations_to_be_held[240]` |
| B33 | hold any short escaped tail (the rule before this fix) | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[e0]` |
| B34 | stray C1 range starts at 81 | caught | `tests/test_bytes_boundaries.py::test_one_stray_byte_is_removed_only_in_the_c1_range[80]` |
| B35 | stray C1 range ends at 9E | caught | `tests/test_bytes_boundaries.py::test_one_stray_byte_is_removed_only_in_the_c1_range[9f]` |
| B36 | stray C1 range ends at A0 | caught | `tests/test_bytes.py::test_invalid_bytes_that_were_already_together_stay` |
| B37 | escaped-byte range starts at 81 | caught | `tests/test_bytes_boundaries.py::test_a_lead_is_held_only_while_its_next_byte_can_continue_it[c2]` |
| B38 | escaped-byte range ends at FE | equivalent | none: byte FF is neither a lead nor a continuation, so the lead table and every continuation range reject it whether or not it counts as escaped. `unjoin` with and without the change gave identical results, final and not final, for all 2,463,459 inputs tried (every string of one to three characters over `a` and the 128 escaped bytes, plus 300,000 seeded strings of four to eight). |

### Decoder lookahead mutations (review round 2)

Each change was applied alone to a scratch copy of the fix commit `b966009`, then the full
suite ran with `-x`, bytecode disabled and a 300-second per-test timeout. Caught means
exit 1 through a test failure. The restored copy passes again (exit 0). L1 and L2 put back
the reported defect.

| Id | Deliberate change | Module | Result | First failing contract |
| --- | --- | --- | --- | --- |
| L1 | `_strip` ignores the decoder's pending bytes (the reviewed behaviour) | `_cli.py` | caught | `tests/test_cli_lookahead.py::test_a_live_stream_writes_a_lead_its_pending_byte_cannot_continue[c2c2]` |
| L2 | `unjoin` ignores its lookahead | `_bytes.py` | caught | `tests/test_cli_lookahead.py::test_a_live_stream_writes_a_lead_its_pending_byte_cannot_continue[c2c2]` |
| L3 | the decoder keeps `ED A0`..`ED BF` pending | `_cli.py` | caught | `tests/test_cli_lookahead.py::test_a_live_stream_writes_a_lead_its_pending_byte_cannot_continue[eda0]` |
| L4 | pending bytes used as lookahead past an open sequence | `_cli.py` | caught | `tests/test_cli_lookahead.py::test_pending_bytes_after_an_open_sequence_are_not_lookahead` |
| L5 | a full-length pending prefix counts as unable to complete | `_bytes.py` | caught | `tests/test_cli.py::test_a_sequence_split_across_reads_is_removed` |

## Tested archive hashes

Preparation wheel SHA-256: `eac999167b8e0b0ef57315e2c450a0c386c78e4e0e87adc65757b5f17e40faa8`.
Preparation sdist SHA-256: `45919bf97970e0c02ad28821cad7d93fa44c6cd19387f679c06a5b4d48595b64`.

## QA round 1

Reviewed base: `9c587d6425bd951a38d09cdcaee9b933dd7c3b61`. Date: 2026-11-01.
Fix commit: `6ffedffaa794a55c8435c4911a383babc9b31dc9` (`fix the first certification findings`).
All nine findings are addressed; independent lens re-verification remains pending.

| Findings | Changes and verification |
| --- | --- |
| A-001, E-06 | Decode Brotli/gzip/deflate before manifest validation. Compressed-response contracts fail before the fix; live fetch now verifies all four unchanged pins. Brotli is development-only. |
| C-01 | Base-type content operations bypass bytes/bytearray buffer hooks. Regressions first fail for substitution, exceptions and large messages in both codecs; stored data and memoryview contracts pass. |
| C-02 | Consume both ST forms before cancellation/keep; hold ESC across chunks. Regressions first fail, then pass for every string family, both codecs, splits, pickle and close. GUIDE/CHANGELOG record the pending-ESC behavior. |
| E-01 | Nondefault and combined options survive repeated close/reuse. M19, M51 and M52 now fail `test_close_preserves_every_option_across_reuse`. |
| E-02 | Bare ESC final-byte boundary and every split are pinned. M26 fails `test_first_final_byte_directly_after_escape_at_every_split`. |
| E-03 | GUIDE pins existing read-error policy: emitted output remains; pending decoder/joining tails are discarded; later files run. M34 fails `test_read_errors_discard_pending_utf8_tails_but_keep_emitted_output`. |
| E-04 | Exact supported names and rejected aliases/case variants are pinned. M39 fails `test_encoding_aliases_are_rejected[utf8]`. |
| E-05 | Raw UTF-8 reports are checked with Latin-1 and non-Latin-1 filenames in both modes and installed entry points. M50 fails `test_installed_wheel_end_to_end`. |

The seven survivor patches were replayed separately in scratch copies: seven assertion failures,
zero survivors or collection errors. All four gates exit 0; strict typing also covers tests.
CPython 3.14.6: 413 passed, no skips, 300-second per-test timeout, both packaging flags enabled.
Public names, signatures and defaults remain unchanged. No findings are disputed.

## QA round 2

Reviewed base: `9f757d095ca73f8daaac809c3786969fd3dc2d47`. Date: 2026-11-01.
Fix commit: `83be0e3a1c11a09f5dde6388d308262f8b49e654` (`pin http fixture decoding contracts`).
All three lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts. The current decoder already has the expected
behavior, so its implementation and the public API remain unchanged. CHANGELOG records
the newly pinned behavior under Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-07 | Test mixed-case Brotli, gzip and deflate names individually and in a three-codec stack. Verify decoded bytes are saved only when the manifest matches. N21 now fails 10 cases of `test_fetch_validates_and_saves_decoded_content`. |
| E-08 | Reject unsupported coding alone and on either side of gzip with a matching decoded-content manifest. Require `ValueError` and an empty destination. N23 now fails all 3 cases of `test_fetch_rejects_unsupported_encoding_without_saving`. |
| E-09 | Pin `identity` as a no-op at the start, middle and end of stacks, including repeated and mixed-case tokens. Continue decoding all remaining codings before validating and saving. N24 now fails 4 cases of `test_fetch_validates_and_saves_decoded_content`. |

The exact N21, N23 and N24 patches were applied separately to scratch copies before and
after adding the contracts. Each originally passed all 12 fetcher tests (exit 0). With
the added contracts each exits 1 through test failures, with no collection errors, skips
or timeouts. The unmodified and restored copies both pass all 33 fetcher tests.

All four release gates exit 0: `ruff format --check .` (38 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (434 passed, no skips). Strict typing also
passes for `src tests` (30 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. A fresh fixture fetch
verified all four unchanged manifest pins; Rich is installed for the oracle test.

## QA round 3

Reviewed base: `b3e481dfd82957ca77085990127d99feb458efa3`. Date: 2026-11-01.
Fix commit: `b9761dfd1b5bbbc396dfffdc7b9427eded47c14e` (`pin whitespace and repeated encoding contracts`).
All three lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts, and the reviewed decoder already passes the
reported behaviors. Its implementation and public API remain unchanged. CHANGELOG records
the added guarantees under Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-10 | Pin horizontal tabs around Brotli, gzip and deflate tokens, alone and in stacks, including mixed spaces and case. R02 now fails 12 cases of `test_fetch_validates_and_saves_decoded_content`. |
| E-11 | Pin trailing spaces on each codec and whitespace before commas in two- and three-codec stacks. R03 now fails 22 cases of `test_fetch_validates_and_saves_decoded_content`. |
| E-12 | Pin twice-compressed gzip, Brotli and deflate bodies, repeated codecs separated by another codec, and mixed-case repeated gzip around `identity`. R08 now fails 6 cases of `test_fetch_validates_and_saves_decoded_content`. |

Each added case verifies both outcomes: a matching manifest saves the exact fully decoded
bytes, and a mismatched manifest rejects the content without saving a fixture.

The exact R02, R03 and R08 patches were replayed separately in scratch copies before and
after adding the contracts. Each originally passed all 33 fetcher tests (exit 0). With
the added contracts, each exits 1 through test failures, without collection errors, skips
or timeouts. Both the unmodified and restored copies pass all 65 fetcher tests.

All four release gates exit 0: `ruff format --check .` (38 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (466 passed, no skips). Strict typing also
passes for `src tests` (30 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. A fresh fixture fetch
verified all four unchanged manifest pins; Rich is installed for the oracle test.

## QA round 4

Reviewed base: `4aaf5cf1d962e8a2d618f6eb8a713fe76ea90c3f`. Date: 2026-11-01.
Fix commit: `cb797236d6fdd4e8ffc2467ad855964f8b80ff1f` (`pin remaining http decoding contracts`).
All seven lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts. The reviewed decoder already implements the
expected behavior, so the implementation and public API remain unchanged. CHANGELOG records
the newly pinned guarantees under Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-13 | Reject internal spaces and tabs in Brotli, gzip, deflate and identity names, alone and inside stacks. Require `ValueError` and an empty destination. N01 fails 10 cases of `test_fetch_rejects_unsupported_encoding_without_saving`. |
| E-14 | Reject semicolon parameters, including an empty parameter suffix, on individual encodings and stacked layers. Require `ValueError` without storage despite a matching decoded-content manifest. N02 fails 8 cases of `test_fetch_rejects_unsupported_encoding_without_saving`. |
| E-15 | Ignore empty list elements before, between and after layers, including whitespace-only elements and identity. Validate and save fully decoded content only when the manifest matches. N03 fails 9 cases of `test_fetch_validates_and_saves_decoded_content`. |
| E-16 | Decode every concatenated gzip member, including empty members and concatenated streams under Brotli. Require exact full-content storage and reject mismatched manifests. N06 fails the concatenated-member cases of `test_fetch_validates_and_saves_decoded_content`. |
| E-17 | Reject gzip streams truncated in their headers, payloads or trailers, both alone and under Brotli. Require `EOFError` and an empty destination, including when a missing trailer still permits all manifest bytes to be emitted. N07 fails `test_fetch_rejects_truncated_gzip_without_saving`. |
| E-18 | Reject mismatches between gzip, Brotli and zlib-wrapped deflate, including gzip labeled deflate under Brotli and raw deflate without its wrapper. Require the corresponding decoder error without storage. N08 fails 2 cases of `test_fetch_rejects_mislabeled_compression_without_saving`. |
| E-19 | Reject incomplete Brotli headers, payloads and final markers, both alone and under gzip. Require `brotli.error` and an empty destination; the missing-marker body emits all expected bytes with an unfinished streaming decoder. N09 fails all 6 cases of `test_fetch_rejects_incomplete_brotli_without_saving`. |

The ten exact N01 through N10 patches were applied separately in scratch copies before
and after adding the contracts. All seven reported survivors originally passed all 65
fetcher tests; N04, N05 and N10 were already caught. With the added contracts, all ten
patches exit 1 through test failures, with no collection errors, skips or timeouts.
The unmodified and restored copies both pass all 137 fetcher tests.

| Mutation | Injected defect | Catching contract | Failing cases |
| --- | --- | --- | --- |
| N01 | Remove internal token whitespace | `test_fetch_rejects_unsupported_encoding_without_saving` | 10 |
| N02 | Discard semicolon parameters | `test_fetch_rejects_unsupported_encoding_without_saving` | 8 |
| N03 | Stop decoding at an empty element | `test_fetch_validates_and_saves_decoded_content` | 9 |
| N04 | Treat any identity layer as wholly unencoded | `test_fetch_validates_and_saves_decoded_content` | 8 |
| N05 | Sort encoding layers | `test_fetch_validates_and_saves_decoded_content` | 38 |
| N06 | Decode only one gzip member | `test_fetch_validates_and_saves_decoded_content` | 17 |
| N07 | Skip gzip completion validation | `test_fetch_rejects_truncated_gzip_without_saving` | 17 |
| N08 | Auto-detect gzip as deflate | `test_fetch_rejects_mislabeled_compression_without_saving` | 2 |
| N09 | Skip Brotli completion validation | `test_fetch_rejects_incomplete_brotli_without_saving` | 6 |
| N10 | Split only the first coding separator | `test_fetch_validates_and_saves_decoded_content` | 34 |

Failure counts include all affected tests; the named contract is one that catches the defect.
All four release gates exit 0: `ruff format --check .` (39 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (538 passed, no skips). Strict typing also
passes for `src tests` (31 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. A fresh fixture fetch
verified all four unchanged manifest pins; Rich is installed for the oracle test.

## QA round 5

Reviewed base: `063539d5245952313c5f4def3ccad61e2e27381a`. Date: 2026-11-01.
Fix commit: `b1e83eee837632ad1eb097ff826976dab9e0b3ae` (`pin byte-exact fixture decoding contracts`).
All six lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts, not incorrect behavior in the reviewed decoder.
The new contracts pass on the unchanged implementation and fail with the reported defects
injected. The public API remains unchanged. CHANGELOG records the guarantees under
Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-20 | Reject deflate streams truncated in the header, payload or any of the four trailer bytes, directly and through fetch, alone and under Brotli. Require `zlib.error` and no saved file, even when the decoded bytes match the manifest. S01 fails 28 cases of the truncated-deflate contracts. |
| E-21 | Corrupt each Adler-32 checksum byte in an otherwise complete stream. Require `zlib.error` directly and through fetch without storage under a matching decoded-content manifest, alone and under Brotli. S02 fails 16 cases of the corrupt-deflate-checksum contracts. |
| E-22 | Decode empty representations and create a zero-byte file under a matching manifest for absent encoding, identity, gzip, deflate, Brotli and a three-codec stack. S04 fails all 12 empty-content cases. |
| E-23 | Preserve CRLF, blank lines and a final carriage return byte-for-byte during decoding and storage across the same six encoding cases. S05 fails all 12 CRLF cases. |
| E-24 | Decode and store complete patterned bodies of 8191, 8192, 8193 and 16385 bytes across the same six encoding cases. S06 fails all 24 cases above the 8192-byte boundary. |
| E-25 | Preserve every byte value and malformed UTF-8 sequences during decoding and storage across the same six encoding cases. S08 fails all 12 binary-content cases. |

The 128 new cases are in `tests/test_fetch_upstream_deflate.py` and
`tests/test_fetch_upstream_bytes.py`. Each representation is handwritten or compressed
locally from handwritten bytes. Successful fetches require exit 0 and exact stored bytes;
rejected streams require the decoder error and an empty destination.

The ten exact S01 through S10 patches were replayed separately in scratch copies before
and after adding the contracts. All six reported survivors originally passed all 137
fetcher tests; S03, S07, S09 and S10 were already caught. With the added contracts, all
ten patches exit 1 through test failures, with no collection errors, skips or timeouts.
The unmodified and restored copies both pass all 265 fetcher tests.

All four release gates exit 0: `ruff format --check .` (41 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (666 passed, no skips). Strict typing also
passes for `src tests` (33 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. A fresh fixture fetch
verified all four unchanged manifest pins; Rich is installed for the oracle test.

## QA round 6

Reviewed base: `aa5a472b8541f4f1767769fc28ac689c9de0df49`. Date: 2026-11-01.
Fix commit: `49f0061e5b6cbeacd04d31c10e4382e3b594ec5b` (`pin fixture storage integrity contracts`).
All six lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts. The added tests pass on the unchanged fetcher
and fail when the reported defects are injected. The implementation and public API remain
unchanged. CHANGELOG records the guarantees under Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-26 | Preserve single and repeated trailing NUL bytes and NUL-only content during decoding and storage across all six encoding cases. N01 fails all 36 corresponding cases of `test_decode_preserves_representation_bytes` and `test_fetch_saves_representation_bytes`. |
| E-27 | Preserve a UTF-8 BOM before text and as the entire representation during decoding and storage across the same encodings. N02 fails all 24 BOM cases of the byte-preservation contracts. |
| E-28 | Use distinct bytes in successive 8192-byte blocks and in the final partial block. Compare complete decoded and saved bytes across the same encodings. N03 fails all 36 distinct-block cases of the byte-preservation contracts. |
| E-29 | Replace both shorter and longer existing fixtures. Fetch twice with unchanged, shorter and empty replacement content. Require exact stored bytes after each successful fetch. N08 fails all 15 cases of `test_fetch_replaces_existing_fixture` and `test_repeated_fetch_replaces_fixture`. |
| E-30 | Keep the correct digest while declaring zero bytes, one byte too few or one byte too many. Require exit 1 and an empty destination. N09 fails all 9 cases of `test_fetch_rejects_wrong_size_with_correct_digest_without_saving`. |
| E-31 | Keep the correct size and alter one digest digit after matching prefixes of 8, 31, 62 or 63 digits. Require exit 1 and an empty destination. N10 fails all 12 cases of `test_fetch_rejects_digest_suffix_mismatch_without_saving`. |

The 132 added cases extend `tests/test_fetch_upstream_bytes.py` and introduce
`tests/test_fetch_upstream_storage.py`. Byte preservation covers absent encoding,
identity, gzip, deflate, Brotli and a three-codec stack. Replacement and independent
manifest checks cover absent encoding, gzip and the three-codec stack. All payloads
are handwritten or compressed locally from handwritten bytes.

The ten exact N01 through N10 patches were replayed serially in a scratch copy before
and after adding the contracts. All six reported survivors originally passed all 265
fetcher tests; N04, N05, N06 and N07 were already caught. With the added contracts, all
ten patches exit 1 through test failures, with no collection errors, skips or timeouts.
The unmodified and restored copies both pass all 397 fetcher tests.

All four release gates exit 0: `ruff format --check .` (42 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (798 passed, no skips). Strict typing also
passes for `src tests` (34 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. A fresh fixture fetch
verified all four unchanged manifest pins; Rich is installed for the oracle test.

## QA round 7

Reviewed base: `355643841a4c5f694149aed36c3fe0dae5eb84b9`. Date: 2026-11-01.
Fix commit: `c421094fed7fb16814f957c35bb6031ee76edd66` (`pin manifest processing contracts`).
All five lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts. The added tests pass on the unchanged fetcher
and fail when the reported defects are injected. The implementation and public API remain
unchanged. CHANGELOG records the guarantees under Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-32 | Fetch a three-entry manifest with distinct text, empty and binary bodies. Require every URL to be requested and every file to contain its own exact bytes. Q06 fails 12 cases, including `test_fetch_saves_every_valid_manifest_entry`. |
| E-33 | Reject the first entry for size or digest mismatch, then process two valid entries. Require final exit status 1. Q07 fails 12 cases, including `test_fetch_keeps_earlier_failure_status_after_success`. |
| E-34 | After a size or digest mismatch, require both later valid entries to be fetched and saved, with no rejected file stored. Q08 fails all 6 cases of `test_fetch_continues_after_rejected_manifest_entry`. |
| E-35 | Prepopulate a fixture with old bytes, then reject a response for a size declared too small, too large or a wrong digest. Require exit 1 and unchanged existing bytes. Q09 fails all 9 cases of `test_fetch_preserves_existing_fixture_when_validation_fails`. |
| E-36 | Explicitly unset `STRIPCONTROL_UPSTREAM`, redirect the manifest directory to a temporary path, and require successful storage beside the manifest. Q10 fails all 3 cases of `test_fetch_defaults_to_manifest_directory_when_destination_is_unset`. |

The 27 added cases introduce `tests/test_fetch_upstream_manifest.py` and extend
`tests/test_fetch_upstream_storage.py`. Each behavior runs with absent encoding, gzip
and a gzip/deflate/Brotli stack. HTTP responses are injected; payloads are handwritten
or compressed locally from handwritten bytes. Temporary files stay in scratch storage.

The exact Q06 through Q10 patches were replayed serially in a scratch copy before and
after adding the contracts. Each originally passed all 397 fetcher tests. With the added
contracts, all five patches exit 1 through test failures, with no collection errors,
skips or timeouts. The unmodified and restored copies both pass all 424 fetcher tests.

All four release gates exit 0: `ruff format --check .` (43 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (825 passed, no skips). Strict typing also
passes for `src tests` (35 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. A fresh fixture fetch
verified all four unchanged manifest pins; Rich is installed for the oracle test.

## QA round 8

Reviewed base: `81c28bce992c2023aa51480e4a94eb383b29d9d8`. Date: 2026-11-01.
Fix commit: `1d47913b33c8057d223145341f3eeac96b660cd5` (`pin manifest rejection and destination contracts`).
All five lens e findings are addressed; independent lens re-verification remains pending.
These findings identify missing contracts. The added tests pass on the unchanged fetcher
and fail when the reported defects are injected. The implementation and public API remain
unchanged. CHANGELOG records the guarantees under Clarified. No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| E-37 | Reject two or three entries for size or digest mismatch and require exactly exit status 1. R01 fails all 12 cases of `test_fetch_returns_status_one_for_multiple_rejections`. |
| E-38 | Require exit status 1 for an even rejection count, while checking every request and the exact remaining files. R02 fails the 6 two-rejection cases of the same contract. |
| E-39 | Reject either the second or third entry for size or digest mismatch after a successful first entry. Require exit 1, complete processing and no rejected file. R03 fails 24 cases, including all 12 cases of `test_fetch_rejects_mismatch_after_successful_entry`. |
| E-40 | Save a valid fixture beneath three missing destination directories and check exact bytes. R04 fails all 3 cases of `test_fetch_creates_missing_destination_ancestors`. |
| E-41 | Write UTF-8 JSON with literal unescaped Latin and Japanese filenames; require successful validation and exact stored names and bytes. R06 fails all 6 cases of `test_fetch_reads_literal_utf8_manifest_filenames`. |

The 33 added cases extend `tests/test_fetch_upstream_manifest.py` and
`tests/test_fetch_upstream_storage.py`. Each behavior runs with absent encoding, gzip
and a gzip/deflate/Brotli stack. HTTP responses are injected; payloads are handwritten
or compressed locally from handwritten bytes. Temporary files stay in scratch storage.

The exact R01, R02, R03, R04 and R06 patches were replayed serially in a scratch copy
before and after adding the contracts. Each originally passed all 424 fetcher tests.
With the added contracts, all five patches exit 1 through test failures, with no
collection errors, skips or timeouts. The unmodified and restored copies both pass
all 457 fetcher tests.

All four release gates exit 0: `ruff format --check .` (43 files), `ruff check .`,
`mypy --strict src` (8 files), and `pytest` (858 passed, no skips). Strict typing also
passes for `src tests` (35 files). CPython 3.14.6, 300-second per-test timeout; both
installed-wheel and live PyPI 0.2.0 upgrade checks are enabled. All four pinned upstream
fixtures and Rich are present for the ground-truth and oracle tests.

## Review round 1

Reviewed base: `12784750127b9dba3fe4ef04ebc492e5914c7acf`. Date: 2026-11-03.
Fix commit: `9d14bd80545bef75af38396906c0adc70b48467d`
(`hold back only utf-8 leads that can still complete and pin every byte boundary`).
The single reviewer finding is addressed; re-review by the same reviewer remains pending.
No findings are disputed.

| Finding | Changes and verification |
| --- | --- |
| F-18 | The two reported mutations (two-byte leads from C0, four-byte leads up to F7) were replayed on the reviewed base: both survive the full suite (exit 0). New `tests/test_bytes_boundaries.py` checks every byte 80..FF: only C2..F4 are held back at the end of a read, while C0, C1 and F5..FF never are; the CLI keeps C0, F5 and every other non-lead A0..FF when the next read fails; a live stream emits them at once. The lead table is handwritten from RFC 3629 and checked against the strict decoder. Closing the class found a related defect: a lead followed by a byte that cannot continue it (`E0 C0`, `ED A0`, `F4 A0`, `F0 A0 C0`, `F4 FF`) was also withheld and lost on a read failure. Contracts for every lead's second-byte range and for later continuation bytes failed on the base (32 cases); `unjoin` now holds back only bytes that can still complete a character. One existing case that pinned the old rule (`F4 A0` withheld) became `F0 A0`, a tail that can still complete. GUIDE and CHANGELOG (Fixed, Clarified) record the change; normal EOF output is unchanged. |

38 byte-boundary mutations, covering both sides of every lead, second-byte, continuation,
stray C1 and escaped-byte range in `_bytes.py`, were replayed one at a time (table under
item 18): 37 caught, one proven equivalent. Public names, signatures and defaults remain
unchanged.

All four release gates exit 0 on this commit: `ruff format --check .` (44 files),
`ruff check .`, `mypy --strict src` (8 files), and `pytest` (1347 passed, 2 skipped: the
installed-wheel and PyPI upgrade checks, which need their opt-in switches). Strict typing
also passes for `src tests` (36 files). CPython 3.13.2, 300-second per-test timeout.

## Review round 2

Reviewed base: `723cf72bf8811c8e27930dcf575881217a983ef5`. Date: 2026-11-03.
Fix commit: `b9660094a30c9b812c52a046f62fe6aef5628a95`
(`write a utf-8 lead at once when the decoder's pending bytes cannot continue it`).
The single reviewer finding is addressed; re-review remains pending. No findings are
disputed.

| Finding | Changes and verification |
| --- | --- |
| F-6 | Confirmed on the reviewed base: the incremental decoder keeps a trailing lead, and the pairs `ED A0`..`ED BF`, in its own buffer, so `unjoin` saw the lead before it with nothing after it and held it back; a read failure lost it. Round 1 above claimed `ED A0` was written; that held for `unjoin` alone but not through the CLI decoder. New `tests/test_cli_lookahead.py` drives `main` through the real decoder: the output seen when the next read starts (stdin kept open) and after that read fails, for `C2 C2`, `E0 F0`, `F4 C2`, `ED A0` and `ED BF`, plus every lead `C2`..`F4` followed by every byte `A0`..`FF` (all 4,896 pairs) against the strict decoder. 11 cases failed on the base. `_decode` now yields the decoder's pending bytes with each chunk and `unjoin` uses them as lookahead, so a lead followed by a pending byte that cannot continue it is written at once. Pending bytes that can never complete (`ED A0`..`ED BF`) are flushed from the decoder and written at once; this is exact because every later byte decodes the same either way. Pending bytes are not used as lookahead while an escape sequence is open, since the bytes after the removed sequence decide whether the lead joins; a new contract pins that (reads `61 C2 1B C2`, where the last `C2` is pending, then `80 BF`: the lead must not join `BF` into `C2 BF`). The reviewer's scripts now report 0 over-held pairs and, by subprocess with stdin open, `61 C2 C2` emits `61 C2`, `61 F4 C2` emits `61 F4`, `61 ED A0` emits `61 ED A0`. GUIDE and CHANGELOG 1.0.0 Fixed record the change and the open-sequence exception; normal EOF output is unchanged. Five lookahead mutations (table under item 18) are all caught. |

`_strip` and `_decode` are private; public names, signatures and defaults are unchanged.

All four release gates exit 0 on the fix commit: `ruff format --check .` (45 files),
`ruff check .`, `mypy --strict src` (8 files), and `pytest` (1359 passed, 2 skipped: the
installed-wheel and PyPI upgrade checks, which need their opt-in switches). Strict typing
also passes for `src tests` (37 files). CPython 3.13.2, 300-second per-test timeout.

## Review round 3

Reviewed base: `ec29b688ff01f51d0a425a301663a170252f32df`. Date: 2026-11-03.
Fix commit: `e4dd0ddfd7d9fa4d4edad91e73989732eca5d67a`
(`keep a lead written through lookahead as context so a removed pending character cannot join it`).
All four release gates exit 0 on the fix commit: `ruff format --check .` (46 files), `ruff check .`,
`mypy --strict src` (8 files) and `pytest`.
The single reviewer finding is addressed; re-review remains pending. No findings are
disputed.

| Finding | Changes and verification |
| --- | --- |
| F-6b | Confirmed on the reviewed base: the pending bytes used as lookahead can complete into a removed character (C1 `C2 80`..`C2 9F`, or a format character with `--format-chars`), so the lead was written with no protection and later continuation bytes joined it (`61 C2 C2 \| 80 BF` gave `61 C2 BF`). New `tests/test_cli_lookahead_removal.py`: five two-read contracts (the reviewer's three cases plus a lead with a continuation byte, `61 E0 A0 C2 \| 80 A0` and its ZWSP variant) and a sweep over every lead `C2`..`F4`, every pending lead `C2`..`F4`, removable completions and four fills, under five option sets, comparing EOF output with `strip_control_bytes` of the whole input; all failed on the base. `_strip` now keeps a lead written through lookahead as context in front of the next text and strips it from the output, so continuation bytes after a removal are still dropped; a lead with continuation bytes after it is written early only when `_bytes.may_be_removed` says no completion of the pending bytes is removed. `tests/test_cli_lookahead.py` and the reviewer's round-2 and round-3 scripts (`join.py`) agree with one read and `strip_control_bytes`. GUIDE and CHANGELOG 1.0.0 state the rule. |

Mutations under item 18 (round 3), against `tests/test_cli_lookahead_removal.py` and `tests/test_cli_lookahead.py`:

| Id | Change | Result |
| --- | --- | --- |
| N1 | written lead never kept as context | caught: c1-joins-c2-bf |
| N2 | lead with tail written regardless of removable pending | caught: c1-tail, zwsp-tail |
| N3 | context left inside the held tail (duplicated) | caught: c1-joins-c2-bf |
| N4 | context dropped while the lead is still held | caught: c1-joins-c2-bf |
| N5 | `may_be_removed` ignores format characters | caught: zwsp-tail |

## Review round 4

Reviewed base: `88e7b9142456a7164f1b5383c28683c4768834fb`. Date: 2026-11-03.
Test commit: `26a5143be4e7b47e1fdc8faee862aeffe8d598c8`
(`test that a written lead stays context across several later reads`). No source change.
All four release gates exit 0 on the test commit: `ruff format --check .` (47 files),
`ruff check .`, `mypy --strict src` (8 files) and `pytest`.
The single reviewer finding is addressed; re-review remains pending. No findings are
disputed.

| Finding | Changes and verification |
| --- | --- |
| F-6c | Confirmed: mutation 12 (`written = lead if len(lead) == 1 else ""`, which drops a written lead after the first later read) survived the whole suite, because no test carried a written lead across more than one later read. The real code was already right. New `tests/test_cli_lookahead_chain.py`: the reviewer's two cases as CLI contracts (reads `F0 C2 \| 9B A0 BB \| A0` give `F0`; with `--format-chars --strip-whitespace`, reads `8B \| C2 C2 E2 \| 80 8B C2 85 \| BB 80 F4` give `C2 C2 F4`), each compared with `strip_control_bytes` of the whole input under the same options; and a seeded property (seed 20261103, 250 inputs of 1 to 12 pieces drawn from continuation and stray C1 bytes, UTF-8 leads, encoded C1 and format characters, ESC, BEL, NUL and whitespace, cut at 1 to 3 random points) run under all 16 option sets the CLI strips with (`--format-chars`, `--strip-whitespace`, `--chars-only`, `--latin-1`), where EOF output must equal `strip_control_bytes`. It runs in about one second. The real code passes all of them. |

Mutation under item 18 (round 4), against the full suite:

| Id | Change | Result |
| --- | --- | --- |
| 12 | `written = lead if len(lead) == 1 else ""` in `_cli._strip` (the lead is not kept as context past one read) | caught: c1-pending-then-two-reads, zwsp-pending-then-two-reads, and the seeded property on its own |

## Final verdicts

Date: 2026-11-03. Release head before this record: `35ba1ba7a89493ddcbfc9c03084992db4c4dee7a`.

### QA lenses (item 19)

Each lens report is kept with the certification evidence, outside the repository.

| Lens | Rounds | Final verdict | Report | Commit |
| --- | --- | --- | --- | --- |
| a. API and docs | 2 | PASS | lens a, round 2 report | `9f757d0` |
| b. Correctness and ground truth | 1 | PASS | lens b, round 1 report | `9c587d6` |
| c. Adversarial and robustness | 2 | PASS | lens c, round 2 report | `9f757d0` |
| d. Packaging and real e2e | 1 | PASS | lens d, round 1 report | `9c587d6` |
| e. Contract strength | 9 | PASS | lens e, round 9 report | `1278475` |

Every finding from earlier rounds is recorded in the QA round sections above and was
re-verified by the same lens.

### Independent reviewer scorecard (item 16)

Round 5 passed at `35ba1ba`. Rounds 1 to 4 failed on F-18, F-6, F-6b and F-6c, each fixed
and recorded in the review round sections above.

| Item | Result |
| --- | --- |
| 1 | PASS |
| 2 | PASS |
| 3 | PASS |
| 4 | PASS |
| 5 | PASS |
| 6 | PASS |
| 7 | PASS |
| 8 | PASS |
| 9 | PASS |
| 10 | PASS |
| 11 | PASS |
| 12 | PASS |
| 13 | PASS |
| 14 | PASS |
| 15 | PASS |
| 16 | PASS |
| 17 | PASS: PR open and guard CLEAN; merge and publication follow |
| 18 | PASS |
| 19 | PASS |
