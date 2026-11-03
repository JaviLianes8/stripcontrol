"""Upgrade the published 0.2.0 wheel in place and verify the compatibility boundary."""

from __future__ import annotations

import os
import sys
import venv
from pathlib import Path

import pytest
from test_e2e_wheel import PROGRAM, _archives, _run

pytestmark = pytest.mark.skipif(
    os.environ.get("STRIPCONTROL_E2E_PYPI") != "1", reason="set STRIPCONTROL_E2E_PYPI=1"
)

BEFORE = r"""
import pickle
from pathlib import Path
from stripcontrol import ControlStripper, strip_control, strip_control_bytes, __version__
assert __version__ == "0.2.0"
assert strip_control("a\x00", sequences=0, format_chars=1) == "a"
try:
    strip_control_bytes(b"", encoding=None)
except ValueError:
    pass
else:
    raise AssertionError("0.2.0 accepted an unsupported encoding")
try:
    strip_control_bytes(b"", encoding="secret")
except ValueError as error:
    assert "secret" in str(error)
stream = ControlStripper()
assert stream.feed("\x1b[3") == ""
Path("stream.pickle").write_bytes(pickle.dumps(stream))
class Buffer(bytes):
    def __bytes__(self):
        return b"custom"
assert strip_control_bytes(Buffer(b"actual")) == b"custom"
"""

AFTER = r"""
import pickle
from pathlib import Path
from stripcontrol import ControlStripper, strip_control, strip_control_bytes, __version__
assert __version__ == "1.0.0"
for call in [lambda: strip_control("", sequences=0),
             lambda: strip_control("", format_chars=1),
             lambda: strip_control_bytes(b"", encoding=None)]:
    try:
        call()
    except TypeError:
        pass
    else:
        raise AssertionError("missing type check")
try:
    strip_control_bytes(b"", encoding="secret")
except ValueError as error:
    assert "secret" not in str(error)
old = pickle.loads(Path("stream.pickle").read_bytes())
assert old.feed("1mvisible") == "visible"
assert ControlStripper.__module__ == "stripcontrol"
class Buffer(bytes):
    def __bytes__(self):
        return b"custom"
assert strip_control_bytes(Buffer(b"actual")) == b"actual"
"""


def test_pypi_upgrade_in_place(tmp_path: Path) -> None:
    wheel, _ = _archives(tmp_path)
    environment = tmp_path / "upgrade"
    venv.create(environment, with_pip=True)
    bindir = environment / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(
        python, "-m", "pip", "install", "--disable-pip-version-check", "stripcontrol==0.2.0"
    )
    assert installed.returncode == 0, installed.stderr
    before = _run(python, "-I", "-c", PROGRAM + BEFORE, cwd=tmp_path)
    assert before.returncode == 0, before.stderr
    script = bindir / ("stripcontrol.exe" if sys.platform == "win32" else "stripcontrol")
    expected = b"abc\n"
    data = b"a\x1b]2;t\x07b\x1b[31mc\n"
    assert _run(script, stdin=data, cwd=tmp_path).stdout == expected
    upgraded = _run(python, "-m", "pip", "install", "--upgrade", "--no-deps", wheel)
    assert upgraded.returncode == 0, upgraded.stderr
    after = _run(python, "-I", "-c", PROGRAM + AFTER, cwd=tmp_path)
    assert after.returncode == 0, after.stderr
    assert _run(script, stdin=data, cwd=tmp_path).stdout == expected
    assert _run(python, "-m", "pip", "check").returncode == 0
