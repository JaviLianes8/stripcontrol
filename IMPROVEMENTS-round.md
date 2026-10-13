# stripcontrol improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: Unicode 18.0 categories, ECMA-48, the DEC parser, xterm control sequences
- [x] Sequence-aware stripping: CSI, OSC, DCS, SOS/PM/APC, ST and BEL, CAN/SUB, C1 forms
- [x] Streaming stripper that keeps state across chunk boundaries
- [x] Bytes input: UTF-8 C1 versus 8-bit C1, stray bytes
- [x] Unicode format characters (Cf) as an option, table generated from the UCD
- [x] Visible escaping for logs (`escape_control`)
- [x] Typed API and contracts: argument checks, runnable README, installed wheel
- [x] Command line: filter and check mode
- [x] Docs and packaging: README, CHANGELOG, metadata, sdist contents
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [x] Mutation run: removing guarded logic makes the suite fail
- [x] Independent review findings fixed with regression tests
- [x] Pull request opened (#2), guard clean

## Starting point

`0.1.0` has `strip_control`, `has_control`, `find_control` and `STANDARD_WHITESPACE`. They
work one character at a time over C0, DEL and C1, which matches the Unicode `Cc` category.
Compared with the sources below:

- Removing only the control characters of an escape sequence leaves its printable body
  behind: `"\x1b[31mred"` becomes `"[31mred"` and a window title change
  `"\x1b]0;pwned\x07"` becomes `"]0;pwned"`. A sanitised log line is still full of noise,
  and the printable payload of an OSC, DCS or APC string (which a terminal never shows) is
  now visible text.
- Nothing knows about the 8-bit forms: `U+009B` is CSI and `U+009D` is OSC, so their
  parameters survive too.
- There is no way to process a stream: a sequence split across two `read()` calls cannot be
  recognised by calling the function per chunk.
- Bytes are not accepted. The tempting fix, dropping every byte from `0x80` to `0x9F`,
  corrupts UTF-8 text (`"Λ"` is `CE 9B`), while a C1 control in UTF-8 is two bytes
  (`C2 9B`).
- Unicode format characters (`Cf`: bidi overrides, zero-width characters, tags) are out of
  reach even though they drive the Trojan Source attack (CVE-2021-42574).
- `keep` and `STANDARD_WHITESPACE` are fixed for `has_control` and `find_control`; a
  non-`str` argument fails with an unrelated error.
- No command line, no runnable docs, no installed-wheel test.

## Sources (fetched 2026-10-13)

None of these files is committed (owner policy: no third-party text in the repository).
`tests/upstream/MANIFEST.json` records URL, revision, size and sha256 for the ones the tests
read, `scripts/fetch_upstream.py` fetches them into the ignored `tests/upstream/` folder, and
their tests skip while they are absent.

- Unicode 18.0.0 `extracted/DerivedGeneralCategory.txt`,
  https://www.unicode.org/Public/18.0.0/ucd/extracted/DerivedGeneralCategory.txt
  (282143 bytes, sha256 d6b151d2d40ee9b1876d26f417980f45ffae47b6055ccf7203cb31f07a030f94).
  `Cc` is exactly `0000..001F` and `007F..009F`; `Cf` is 21 ranges, 170 code points.
- ECMA-48 5th edition (June 1991),
  https://ecma-international.org/wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf
  (sha256 9577ad2514c411584b274ef7a4b3238c80aa93defbb349b18b8c78f78873f450). 5.3 escape
  sequences, 5.4 control sequences (parameter bytes 03/00 to 03/15, intermediate bytes
  02/00 to 02/15, final byte 04/00 to 07/14), 5.6 control strings closed by ST, 8.3.128 SOS.
- Paul Flo Williams, "A parser for DEC's ANSI-compatible video terminals",
  https://vt100.net/emu/dec_ansi_parser
  (sha256 72db5905ebd81bb4f3da420db66db390bfa6693704bc5e24aec74290d2ce691d). How a real
  terminal recovers: ESC, CAN, SUB and every C1 control cancel a sequence in progress, C0
  controls are executed inside escape and control sequences and ignored inside strings.
- XTerm Control Sequences, patch #411 (2026/08/23),
  https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
  (sha256 b4c4fbe5738b82c91860b924c8c0ae1afbacf637b4184f98b0382e0e8f033475). The 7-bit and
  8-bit C1 pairs, and BEL as an OSC terminator next to ST.
- NVD records read through the NVD 2.0 API
  (`https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=<id>`): CVE-2009-4487 (nginx) and
  CVE-2009-4492 (WEBrick) wrote request data with escape sequences to log files, letting a
  remote client retitle the window of whoever reads the log; CVE-2021-25743 (kubectl) printed
  object fields with raw escape sequences; CVE-2021-42574 (Trojan Source) reorders source
  code with bidi format characters.

## Ranked improvements

1. **Remove whole sequences, not just their control characters.** A small state machine
   modelled on the DEC parser: ESC sequences (`ESC I* F`), CSI (`ESC [` or `U+009B`, then
   parameters, intermediates, final), OSC (`ESC ]`, `U+009D`, ended by ST or BEL), DCS,
   SOS, PM and APC (ended by ST), cancelled by CAN, SUB, ESC or any C1 control. An
   unterminated sequence is dropped to the end, as a terminal would swallow it. Hard
   contract: the output never holds a control character outside `keep`, whatever the input.
   On by default (`sequences=False` restores the per-character mode).
2. **Linear time on hostile input.** Runs of ordinary text and string payloads are skipped
   with one regex search each; no backtracking pattern ever spans a sequence. Tested with
   1 MB of each adversarial shape (unterminated OSC openers, CSI without final, ESC runs,
   C1 runs, alternating openers).
3. **Streaming.** `ControlStripper.feed(chunk)` returns the clean text so far and keeps the
   parser state, so a sequence split anywhere across chunks is removed exactly as in one
   call. Contract: every split of a fuzzed corpus gives the one-shot result.
4. **Bytes and the two C1 encodings.** `strip_control_bytes(data, encoding="utf-8")` treats
   `C2 80..C2 9F` as C1 and leaves `CE 9B` alone; a stray byte `80..9F` that is not part of a
   UTF-8 character is removed (an 8-bit terminal would act on it) and other invalid bytes
   pass through. `encoding="latin-1"` reads every byte `80..9F` as C1.
5. **Format characters.** `format_chars=True` also removes `Cf` (bidi overrides and
   isolates, zero-width characters, the BOM, tags). The table is generated from the pinned
   UCD file, so results do not depend on the interpreter's `unicodedata` version, and a test
   compares it with the file.
6. **Visible escaping.** `escape_control` turns each control into `\xNN` or `\uNNNN` so a
   log keeps the evidence without the effect.
7. **Typed API and docs.** `keep` and `format_chars` on every function, `TypeError` for
   non-text arguments, README examples executed by the tests, API table checked against
   `__all__`, `mypy --strict` clean.
8. **Command line.** `stripcontrol [FILE ...]` streams files or stdin to stdout,
   `--check` exits 1 and lists positions when anything would be removed, `--escape`,
   `--chars-only`, `--format-chars`, `--strip-whitespace`, `--latin-1`.
9. **Packaging.** Version 0.2.0, classifiers and keywords, console script, sdist without
   planning notes or fetched files, installed-wheel end-to-end test.

## Out of scope

- Line and paragraph separators (`U+2028`, `U+2029`): they are not controls, though a
  per-field log sanitiser may want them gone; `keep=""` plus a `str.replace` covers it.
- Keeping colours while removing everything else (an SGR allow-list): a different product.
- Emoji-aware `Cf` handling: `format_chars=True` removes ZWJ and tag characters, which
  breaks emoji sequences; this is documented rather than special-cased.

## Verification

- Gates on CPython 3.14 (a second Windows machine, fresh clone of the branch, new venv):
  `ruff format --check .`, `ruff check .`, `mypy --strict src` (and `src tests`) and
  `pytest` with the pinned files fetched and `STRIPCONTROL_E2E=1`: 174 passed. The
  installed-wheel test builds the wheel and sdist, checks their contents, installs the wheel
  in a fresh venv and drives the API, the `stripcontrol` console script and
  `python -m stripcontrol` from an empty folder. Without the fetched files their tests skip.
- Pinned sources: the `Cc` set of the UCD file is exactly what counts as a control, the
  generated `Cf` table equals the file and agrees with the interpreter's `unicodedata`, and
  each of the 16 C1 pairs listed by xterm strips the same in 7-bit and 8-bit form.
- Mutation runs (one source edit at a time, no bytecode, per-mutant timeout, suite green
  before and after). First run, 89 mutants: 14 alive. Equivalent code was removed (the C1
  check that the non-ASCII branch already covers, the BEL check that only an OSC can reach,
  a second `keep` check, a dead `close()` call, a `continue`), and tests were added for the
  byte boundaries the survivors exposed (US inside CSI, which also made the parser stall,
  `@` as final, `/` as intermediate, `ESC ( 0`), the decoder flush at end of input, a control
  and a stray byte in one read, and flushing. Second run after the review fixes, 96 mutants:
  one alive (four-byte joins), now killed by a test.

## Review fixes

An independent review attacked the branch; each finding is fixed with a test that fails
without the fix:

- Removing a control between invalid bytes could join them into a valid character, so
  `EF BB 00 BF` came out as a byte order mark even with `format_chars=True`, in
  `strip_control_bytes` and the command line. Escaped bytes that removal joins into a
  character are now dropped, also across reads.
- `--check` printed a file name's undecodable bytes raw (a stray `9B` is an 8-bit CSI).
  Names now show controls, format characters and lone surrogates as escapes.
- A read error was taken for a closed pipe (EINVAL) or ended the run with a traceback
  (EIO). Read and open errors are now reported per input with exit code 2 and the other
  inputs still run; only write errors count as a closed pipe.
- `--chars-only` with `--check` or `--escape` is refused instead of ignored.
- Docs: the line feed rule in the changelog, a kept BEL still ends an OSC, `keep` cannot
  keep a stray byte, `--escape` shows a stray `9B` and U+009B alike, exit codes; module
  docstrings for the CLI tests and fixtures; the xterm check matches the page's OSC syntax
  lines instead of a sentence.
