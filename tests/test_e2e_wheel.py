"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with STRIPCONTROL_E2E=1.
"""

from __future__ import annotations

import email.parser
import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("STRIPCONTROL_E2E") != "1", reason="set STRIPCONTROL_E2E=1 to build and install"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources
import stripcontrol
from stripcontrol import (
    ControlStripper, escape_control, find_control, has_control, strip_control,
    strip_control_bytes,
)

assert "site-packages" in stripcontrol.__file__, stripcontrol.__file__
assert importlib.metadata.version("stripcontrol") == stripcontrol.__version__
assert importlib.resources.files("stripcontrol").joinpath("py.typed").is_file()
assert stripcontrol.UNICODE_VERSION == "18.0.0"
assert strip_control("a\x1b]2;t\x07b\x9b1mc\x00\n") == "abc\n"
assert strip_control("a" + chr(0x202E) + "b", format_chars=True) == "ab"
assert strip_control_bytes(b"\xce\x9b\xc2\x9b1m\x9b") == b"\xce\x9b"
stripper = ControlStripper()
assert stripper.feed("x\x1b[3") + stripper.feed("1my") + stripper.close() == "xy"
assert find_control("a\x1b") == [(1, 27)] and has_control("\x7f")
assert escape_control("\x1b") == "\\x1b"
for call in (lambda: strip_control(b"x"), lambda: strip_control_bytes("x")):
    try:
        call()
    except TypeError:
        pass
    else:
        raise AssertionError("expected TypeError")
print("e2e ok")
"""


def _run(
    *cmd: str | Path, cwd: Path | None = None, stdin: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    env = {
        key: value for key, value in os.environ.items() if key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    return subprocess.run(
        [str(c) for c in cmd],
        cwd=cwd,
        input=stdin,
        capture_output=True,
        check=False,
        timeout=180,
        env=env,
    )


def _archives(tmp_path: Path) -> tuple[Path, Path]:
    if os.environ.get("STRIPCONTROL_WHEEL"):
        return Path(os.environ["STRIPCONTROL_WHEEL"]), Path(os.environ["STRIPCONTROL_SDIST"])
    dist = tmp_path / "dist"
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("stripcontrol-*.whl")
    (sdist,) = dist.glob("stripcontrol-*.tar.gz")
    return wheel, sdist


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    wheel, sdist = _archives(tmp_path)
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata = email.parser.BytesParser().parsebytes(
            archive.read("stripcontrol-1.0.0.dist-info/METADATA")
        )
    assert metadata["Version"] == "1.0.0"
    assert metadata["Requires-Python"] == ">=3.10"
    assert metadata["License-Expression"] == "MIT"
    assert "Development Status :: 5 - Production/Stable" in metadata.get_all("Classifier", [])
    assert all("extra ==" in item for item in metadata.get_all("Requires-Dist", []))
    assert "stripcontrol-1.0.0.dist-info/licenses/LICENSE" in names
    assert "stripcontrol/py.typed" in names
    assert "stripcontrol/_format_table.py" in names
    assert not any(name.startswith(("tests/", "scripts/")) for name in names)
    with tarfile.open(sdist) as archive:
        listing = archive.getnames()
    assert not any("IMPROVEMENTS-round" in name for name in listing)
    assert not any(
        "CERT-" in name or "__pycache__" in name or name.endswith(".pyc") for name in listing
    )
    assert not any(name.endswith((".html", "DerivedGeneralCategory.txt")) for name in listing)
    assert not any(name.endswith((".pdf", ".log")) for name in listing)
    assert any(name.endswith("/LICENSE") for name in listing)
    assert any(name.endswith("tests/upstream/MANIFEST.json") for name in listing)
    assert any(name.endswith("tests/test_sequences.py") for name in listing)

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(python, "-m", "pip", "install", "-q", wheel)
    assert installed.returncode == 0, installed.stderr

    # Run from an empty folder so the source tree cannot shadow the install.
    work = tmp_path / "work"
    work.mkdir()
    result = _run(python, "-I", "-B", "-c", PROGRAM, cwd=work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode().strip() == "e2e ok"

    log = b"GET /\x1b]2;owned\x07 ok\n\xce\x9b\x9b\n"
    script = bindir / ("stripcontrol.exe" if sys.platform == "win32" else "stripcontrol")
    cli = _run(script, cwd=work, stdin=log)
    assert (cli.returncode, cli.stdout) == (0, b"GET / ok\n\xce\x9b\n")
    (work / "access.log").write_bytes(log)
    check = _run(python, "-B", "-m", "stripcontrol", "--check", "access.log", cwd=work)
    assert check.returncode == 1
    assert check.stdout.splitlines() == [
        b"access.log:1:6: U+001B",
        b"access.log:1:15: U+0007",
        b"access.log:2:2: byte 0x9b",
    ]
    for name in ("\u00e9.log", "\u65e5.log"):
        (work / name).write_bytes(b"x\x00")
        for options in ([], ["--latin-1"]):
            for command in ([script], [python, "-m", "stripcontrol"]):
                report = _run(*command, "--check", *options, name, cwd=work)
                assert report.returncode == 1, report.stderr
                assert report.stdout == name.encode("utf-8") + b":1:2: U+0000\n"
                assert report.stderr == b""
    escaped = _run(script, "--escape", cwd=work, stdin=log)
    assert escaped.stdout == b"GET /\\x1b]2;owned\\x07 ok\n\xce\x9b\\x9b\n"
    assert escaped.returncode == 0
    assert _run(script, "--check", "--escape", cwd=work).returncode == 2
    assert _run(script, "--latin-1", stdin=b"a\x9b31mb", cwd=work).stdout == b"ab"
    assert _run(script, "--chars-only", stdin=b"a\x1b[31mb", cwd=work).stdout == b"a[31mb"
    assert _run(script, "--strip-whitespace", stdin=b"a\t\r\nb", cwd=work).stdout == b"ab"
    assert _run(script, "--format-chars", stdin="a\u202eb".encode(), cwd=work).stdout == b"ab"
    assert _run(script, "--check", stdin=b"clean", cwd=work).returncode == 0
    missing = _run(script, "missing.log", "access.log", cwd=work)
    assert missing.returncode == 2 and missing.stdout == b"GET / ok\n\xce\x9b\n"
    assert _run(script, "--help", cwd=work).returncode == 0

    # A real reader closes its end; no device files or timing assumptions are needed.
    (work / "large.log").write_bytes(b"a" * (1 << 20))
    with subprocess.Popen(
        [str(script), "large.log"], cwd=work, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as process:
        assert process.stdout is not None and process.stderr is not None
        process.stdout.close()
        assert process.wait(timeout=30) == 0
        assert process.stderr.read() == b""
