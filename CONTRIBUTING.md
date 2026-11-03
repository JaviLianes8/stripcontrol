# Contributing

Thanks for taking the time. This project keeps a small, predictable shape.

## Setup

```
pip install -r requirements-dev.txt
```

## Before you open a pull request

- Keep public API in `src/stripcontrol/__init__.py`; internals live in `_`-prefixed modules.
- Add a test for the behaviour you change. Use temporary paths for file tests.
  Downloaded sources and the wheel/PyPI checks are opt-in; ordinary tests run offline.
- Pass `pytest --basetemp <scratch-folder>` to select the test workspace. The suite
  requires `pytest-timeout` and limits each test to 300 seconds.
- Run `scripts/check.ps1` (format, lint, types, tests) and make sure it passes.
- One logical change per commit, imperative subject line.

Open an issue first if the change is large or shifts the public API.
