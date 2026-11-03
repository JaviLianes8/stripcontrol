"""Fixtures for the third-party files listed in tests/upstream/MANIFEST.json."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

MANIFEST = Path(__file__).resolve().parent / "upstream" / "MANIFEST.json"
UPSTREAM = Path(os.environ.get("STRIPCONTROL_UPSTREAM", str(MANIFEST.parent)))


def read_upstream(name: str) -> str:
    """Return a third-party file as text, checked against tests/upstream/MANIFEST.json.

    The files are not committed: `python scripts/fetch_upstream.py` fetches them. Their
    tests skip while a file is absent and fail if it differs from the manifest.
    """
    path = UPSTREAM / name
    if not path.is_file():
        pytest.skip(f"{name} is not fetched; run python scripts/fetch_upstream.py")
    entry = json.loads(MANIFEST.read_text(encoding="utf-8"))[name]
    body = path.read_bytes()
    assert len(body) == entry["size"], f"{name} differs from MANIFEST"
    assert hashlib.sha256(body).hexdigest() == entry["sha256"], f"{name} differs from MANIFEST"
    return body.decode("utf-8")


@pytest.fixture(scope="session")
def general_category() -> str:
    """Unicode 18.0.0 DerivedGeneralCategory.txt, see tests/upstream/MANIFEST.json."""
    return read_upstream("unicode-18-DerivedGeneralCategory.txt")


@pytest.fixture(scope="session")
def xterm_ctlseqs() -> str:
    """XTerm Control Sequences (patch #411), see tests/upstream/MANIFEST.json."""
    return read_upstream("xterm-ctlseqs.html")
