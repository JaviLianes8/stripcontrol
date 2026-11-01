"""Handwritten fixtures pin replacement and independent manifest checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_fetch_upstream import BODY, _prepare_fetch, fetch_upstream
from test_fetch_upstream_bytes import _wire

pytestmark = pytest.mark.parametrize("coding", ["", "gzip", "gzip, deflate, br"])


@pytest.mark.parametrize(
    "previous",
    [
        pytest.param(b"old", id="shorter-existing"),
        pytest.param(b"longer old content" * len(BODY), id="longer-existing"),
    ],
)
def test_fetch_replaces_existing_fixture(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, previous: bytes
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, _wire(BODY, coding))
    destination.mkdir()
    fixture = destination / "reference.txt"
    fixture.write_bytes(previous)

    assert fetch_upstream.main() == 0
    assert fixture.read_bytes() == BODY


@pytest.mark.parametrize(
    "replacement",
    [
        pytest.param(BODY, id="unchanged"),
        pytest.param(b"new shorter fixture", id="shorter"),
        pytest.param(b"", id="empty"),
    ],
)
def test_repeated_fetch_replaces_fixture(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, replacement: bytes
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, _wire(BODY, coding))
    fixture = destination / "reference.txt"
    assert fetch_upstream.main() == 0
    assert fixture.read_bytes() == BODY

    _prepare_fetch(monkeypatch, tmp_path, coding, _wire(replacement, coding), body=replacement)
    assert fetch_upstream.main() == 0
    assert fixture.read_bytes() == replacement


@pytest.mark.parametrize("size", [0, len(BODY) - 1, len(BODY) + 1])
def test_fetch_rejects_wrong_size_with_correct_digest_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, size: int
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, _wire(BODY, coding))
    manifest_path = tmp_path / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["reference.txt"]["size"] = size
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert fetch_upstream.main() == 1
    assert list(destination.iterdir()) == []


@pytest.mark.parametrize("position", [8, 31, 62, 63])
def test_fetch_rejects_digest_suffix_mismatch_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, position: int
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, _wire(BODY, coding))
    manifest_path = tmp_path / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = manifest["reference.txt"]["sha256"]
    digit = "1" if digest[position] == "0" else "0"
    manifest["reference.txt"]["sha256"] = digest[:position] + digit + digest[position + 1 :]
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    assert fetch_upstream.main() == 1
    assert list(destination.iterdir()) == []
