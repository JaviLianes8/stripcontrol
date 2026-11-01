# stripcontrol 1.0.0 certification report

Date: 2026-11-01. Preparation resumed from 296c781; main is aacacb6.
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
- [ ] Built wheel, sdist inspection, upgrade, Python matrix (items 8, 10, 14)
- [ ] Final separate gates (item 15)
- [ ] Mutation round and table (item 18)
- [ ] PR and guard
- [ ] Independent reviewer (item 16, pending)
- [ ] Merge and publication (item 17, pending)
- [ ] Five independent QA lenses (item 19, pending)

## API and behavior

The same eight names, signatures and defaults as 0.2.0 are retained. New runtime checks
require actual booleans and distinguish wrong encoding types from unsupported strings.
Errors never quote input values. Text and buffer subclasses use stored data. CLI diagnostics
are bounded; closed output pipes close without a device file. All differences appear in
CHANGELOG 1.0.0 and GUIDE. Existing text and byte filtering rules are unchanged.

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

## Current checks

258 passed, one optional wheel test skipped. Seeds 117/90210 cover 3,000 character cases;
73/314159 cover 5,000 byte cases; 20261101 covers 400 CLI streams with random read sizes;
808 covers the 1,000 Rich comparisons. Existing stream split tests, nine 1 MiB hostile
shapes and a 4 MiB control string also pass. Every test has a 300-second timeout.
