"""Handwritten manifests pin complete processing, failure status and default storage."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

import pytest
from test_fetch_upstream import _Response, fetch_upstream
from test_fetch_upstream_bytes import _wire

pytestmark = pytest.mark.parametrize("coding", ["", "gzip", "gzip, deflate, br"])
BODIES = {"first.txt": b"first fixture\n", "empty.txt": b"", "last.bin": b"last\x00\xff"}


def _prepare_manifest(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    coding: str,
    mismatch: str = "",
) -> tuple[Path, list[str]]:
    manifest = {
        name: {
            "url": f"https://example.test/{name}",
            "size": len(body) + int(name == "first.txt" and mismatch == "size"),
            "sha256": hashlib.sha256(
                b"different" if name == "first.txt" and mismatch == "digest" else body
            ).hexdigest(),
        }
        for name, body in BODIES.items()
    }
    (tmp_path / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    destination = tmp_path / "download"
    monkeypatch.setattr(fetch_upstream, "FOLDER", tmp_path)
    monkeypatch.setenv("STRIPCONTROL_UPSTREAM", str(destination))
    requested: list[str] = []
    responses = {f"https://example.test/{name}": body for name, body in BODIES.items()}

    def urlopen(url: str, *, timeout: int) -> _Response:
        requested.append(url)
        return _Response(_wire(responses[url], coding), coding)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    return destination, requested


def test_fetch_saves_every_valid_manifest_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str
) -> None:
    destination, requested = _prepare_manifest(monkeypatch, tmp_path, coding)

    assert fetch_upstream.main() == 0
    assert requested == [f"https://example.test/{name}" for name in BODIES]
    assert {path.name: path.read_bytes() for path in destination.iterdir()} == BODIES


@pytest.mark.parametrize("mismatch", ["size", "digest"])
def test_fetch_keeps_earlier_failure_status_after_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, mismatch: str
) -> None:
    _prepare_manifest(monkeypatch, tmp_path, coding, mismatch)

    assert fetch_upstream.main() == 1


@pytest.mark.parametrize("mismatch", ["size", "digest"])
def test_fetch_continues_after_rejected_manifest_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, mismatch: str
) -> None:
    destination, requested = _prepare_manifest(monkeypatch, tmp_path, coding, mismatch)

    assert fetch_upstream.main() == 1
    assert requested == [f"https://example.test/{name}" for name in BODIES]
    assert {path.name: path.read_bytes() for path in destination.iterdir()} == {
        name: body for name, body in BODIES.items() if name != "first.txt"
    }


def test_fetch_defaults_to_manifest_directory_when_destination_is_unset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str
) -> None:
    destination, _ = _prepare_manifest(monkeypatch, tmp_path, coding)
    monkeypatch.delenv("STRIPCONTROL_UPSTREAM")

    assert fetch_upstream.main() == 0
    for name, body in BODIES.items():
        assert (tmp_path / name).read_bytes() == body
    assert not destination.exists()


def _reject_entries(tmp_path: Path, names: tuple[str, ...], mismatch: str) -> None:
    manifest_path = tmp_path / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name in names:
        if mismatch == "size":
            manifest[name]["size"] += 1
        else:
            manifest[name]["sha256"] = hashlib.sha256(b"different").hexdigest()
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


@pytest.mark.parametrize("count", [2, 3])
@pytest.mark.parametrize("mismatch", ["size", "digest"])
def test_fetch_returns_status_one_for_multiple_rejections(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, count: int, mismatch: str
) -> None:
    destination, requested = _prepare_manifest(monkeypatch, tmp_path, coding)
    rejected = tuple(BODIES)[:count]
    _reject_entries(tmp_path, rejected, mismatch)

    assert fetch_upstream.main() == 1
    assert requested == [f"https://example.test/{name}" for name in BODIES]
    assert {path.name: path.read_bytes() for path in destination.iterdir()} == {
        name: body for name, body in BODIES.items() if name not in rejected
    }


@pytest.mark.parametrize("rejected", ["empty.txt", "last.bin"])
@pytest.mark.parametrize("mismatch", ["size", "digest"])
def test_fetch_rejects_mismatch_after_successful_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, rejected: str, mismatch: str
) -> None:
    destination, requested = _prepare_manifest(monkeypatch, tmp_path, coding)
    _reject_entries(tmp_path, (rejected,), mismatch)

    assert fetch_upstream.main() == 1
    assert requested == [f"https://example.test/{name}" for name in BODIES]
    assert {path.name: path.read_bytes() for path in destination.iterdir()} == {
        name: body for name, body in BODIES.items() if name != rejected
    }
