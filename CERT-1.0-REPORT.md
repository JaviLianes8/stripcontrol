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
- [x] Mutation round and table (item 18): 29 of 29 caught
- [x] [PR #3](https://github.com/JaviLianes8/stripcontrol/pull/3), `release/1.0.0`; guard CLEAN
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
| 19 | Round 1 lenses a, c, e and rounds 2 through 6 lens e findings fixed below; re-verification pending |

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
