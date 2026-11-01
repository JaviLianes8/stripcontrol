"""Handwritten byte payloads pin exact decoding and manifest-validated storage."""

from __future__ import annotations

import gzip
import zlib
from pathlib import Path

import brotli  # type: ignore[import-untyped]
import pytest
from test_fetch_upstream import _prepare_fetch, fetch_upstream

pytestmark = [
    pytest.mark.parametrize(
        "body",
        [
            pytest.param(b"", id="empty"),
            pytest.param(b"first\r\nsecond\r\n\r\nlast\r", id="crlf"),
            pytest.param(bytes(range(256)) + b"\xff\x00\xc0\xaf\xed\xa0\x80", id="binary"),
            *[
                pytest.param((b"0123456789abcdef" * 1025)[:size], id=f"size-{size}")
                for size in (8191, 8192, 8193, 16385)
            ],
        ],
    ),
    pytest.mark.parametrize(
        "coding", ["", "identity", "gzip", "deflate", "br", "gzip, deflate, br"]
    ),
]


def _wire(body: bytes, coding: str) -> bytes:
    representations: dict[str, bytes] = {
        "": body,
        "identity": body,
        "gzip": gzip.compress(body, mtime=0),
        "deflate": zlib.compress(body),
        "br": brotli.compress(body),
        "gzip, deflate, br": brotli.compress(zlib.compress(gzip.compress(body, mtime=0))),
    }
    return representations[coding]


def test_decode_preserves_representation_bytes(body: bytes, coding: str) -> None:
    assert fetch_upstream._decode(_wire(body, coding), coding) == body


def test_fetch_saves_representation_bytes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, body: bytes, coding: str
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, _wire(body, coding), body=body)
    assert fetch_upstream.main() == 0
    assert (destination / "reference.txt").read_bytes() == body
