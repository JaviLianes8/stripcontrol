"""Locally compressed handwritten content pins deflate completion and checksums."""

from __future__ import annotations

import zlib
from pathlib import Path

import brotli  # type: ignore[import-untyped]
import pytest
from test_fetch_upstream import _prepare_fetch, fetch_upstream

BODY = b"Handwritten deflate reference content.\n"
DEFLATE = zlib.compress(BODY)


@pytest.fixture(
    params=[
        pytest.param(DEFLATE[:1], id="partial-header"),
        pytest.param(DEFLATE[:2], id="header-only"),
        pytest.param(DEFLATE[: len(DEFLATE) // 2], id="partial-payload"),
        *[
            pytest.param(DEFLATE[:-missing], id=f"trailer-missing-{missing}")
            for missing in (4, 3, 2, 1)
        ],
    ]
)
def truncated(request: pytest.FixtureRequest) -> bytes:
    wire: bytes = request.param
    return wire


@pytest.fixture(params=[1, 2, 3, 4], ids=lambda offset: f"checksum-byte-{offset}")
def corrupt_checksum(request: pytest.FixtureRequest) -> bytes:
    wire = bytearray(DEFLATE)
    wire[-request.param] ^= 1
    return bytes(wire)


@pytest.fixture(params=[False, True], ids=["deflate", "deflate-under-brotli"])
def outer_layer(request: pytest.FixtureRequest) -> bool:
    wrapped: bool = request.param
    return wrapped


def _encoded(wire: bytes, outer_layer: bool) -> tuple[str, bytes]:
    if outer_layer:
        return "deflate, br", brotli.compress(wire)
    return "deflate", wire


def test_decode_rejects_truncated_deflate(truncated: bytes, outer_layer: bool) -> None:
    coding, wire = _encoded(truncated, outer_layer)
    with pytest.raises(zlib.error):
        fetch_upstream._decode(wire, coding)


def test_fetch_rejects_truncated_deflate_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, truncated: bytes, outer_layer: bool
) -> None:
    coding, wire = _encoded(truncated, outer_layer)
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire, body=BODY)
    with pytest.raises(zlib.error):
        fetch_upstream.main()
    assert list(destination.iterdir()) == []


def test_decode_rejects_corrupt_deflate_checksum(
    corrupt_checksum: bytes, outer_layer: bool
) -> None:
    coding, wire = _encoded(corrupt_checksum, outer_layer)
    with pytest.raises(zlib.error):
        fetch_upstream._decode(wire, coding)


def test_fetch_rejects_corrupt_deflate_checksum_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, corrupt_checksum: bytes, outer_layer: bool
) -> None:
    coding, wire = _encoded(corrupt_checksum, outer_layer)
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire, body=BODY)
    with pytest.raises(zlib.error):
        fetch_upstream.main()
    assert list(destination.iterdir()) == []
