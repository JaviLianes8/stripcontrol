# stripcontrol 1.0.0 certification report

The 1.0.0 certification bar applied to stripcontrol. PyPI has 0.2.0 (the only release);
`main` is at aacacb6. Whether the published wheel matches `main` byte for byte is still to
be checked, and every behaviour change made here goes in the CHANGELOG.

Progress:
- [x] Branch `release/1.0.0` created from `main` (aacacb6)
- [ ] Baseline gates on 0.2.0, PyPI 0.2.0 compared with `main`
- [ ] API review and 1.0.0 changes (item 1)
- [ ] Errors, typing, docstrings and doctests (items 2 to 5)
- [ ] Ground truth: sources fetched live, reference implementations (item 7)
- [ ] Contract, fuzz and author mutation round (items 6, 9, 18)
- [ ] Docs: README, CHANGELOG (items 11, 12)
- [ ] Packaging, e2e and upgrade from PyPI 0.2.0, every Python (items 8, 10, 13, 14)
- [ ] Gates (item 15)
- [ ] PR and trace guard
- [ ] Five QA lenses (item 19)
- [ ] Independent reviewer (item 16)

## First reading of 0.2.0 (to be reproduced before acting on it)

- No public docstring has a runnable example; there are no doctests.
- The README links LICENSE with a relative path, which breaks on PyPI; it has no
  certified badge and no link to the CHANGELOG.
- pyproject: version 0.2.0, `Development Status :: 4 - Beta`, no `Source` project URL.
- `scripts/release.ps1` refuses any upload once the name exists on PyPI, so it cannot
  publish 1.0.0.
- The installed-wheel test does not install PyPI 0.2.0 and upgrade it in place.
- Fuzzing is limited to the seeded corpora in `tests/test_stream.py`; bytes, the
  command line and `escape_control` have no seeded property tests.
- Ground truth already pinned: Unicode 18.0.0 DerivedGeneralCategory.txt and XTerm
  Control Sequences (patch #411), fetched 2026-10-13, manifest in `tests/upstream`.
