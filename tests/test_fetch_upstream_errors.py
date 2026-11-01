"""Locally compressed handwritten bodies pin rejection before fixture storage."""

from __future__ import annotations

import gzip
import zlib
from pathlib import Path

import brotli  # type: ignore[import-untyped]
import pytest
from test_fetch_upstream import _prepare_fetch, fetch_upstream

BODY = b"Handwritten content.\n"
GZIP = gzip.compress(BODY, mtime=0)
BROTLI = brotli.compress(BODY, quality=0)


def _raw_deflate() -> bytes:
    compressor = zlib.compressobj(wbits=-15)
    return compressor.compress(BODY) + compressor.flush()


@pytest.mark.parametrize(
    "cut",
    [
        pytest.param(2, id="magic-only"),
        pytest.param(9, id="partial-header"),
        pytest.param(len(GZIP) // 2, id="partial-payload"),
        pytest.param(-8, id="missing-trailer"),
        pytest.param(-4, id="partial-trailer"),
        pytest.param(-1, id="last-byte-missing"),
    ],
)
@pytest.mark.parametrize("outer_layer", [False, True])
def test_fetch_rejects_truncated_gzip_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, cut: int, outer_layer: bool
) -> None:
    coding, wire = "gzip", GZIP[:cut]
    if outer_layer:
        coding, wire = "gzip, br", brotli.compress(wire)
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire, body=BODY)
    with pytest.raises(EOFError):
        fetch_upstream.main()
    assert list(destination.iterdir()) == []


@pytest.mark.parametrize(
    ("coding", "wire", "error"),
    [
        pytest.param("deflate", GZIP, zlib.error, id="gzip-as-deflate"),
        pytest.param("gzip", zlib.compress(BODY), gzip.BadGzipFile, id="deflate-as-gzip"),
        pytest.param("br", GZIP, brotli.error, id="gzip-as-brotli"),
        pytest.param("gzip", BROTLI, gzip.BadGzipFile, id="brotli-as-gzip"),
        pytest.param("deflate", BROTLI, zlib.error, id="brotli-as-deflate"),
        pytest.param("br", zlib.compress(BODY), brotli.error, id="deflate-as-brotli"),
        pytest.param("deflate", _raw_deflate(), zlib.error, id="raw-deflate-without-zlib"),
        pytest.param(
            "deflate, br", brotli.compress(GZIP), zlib.error, id="gzip-as-deflate-under-brotli"
        ),
    ],
)
def test_fetch_rejects_mislabeled_compression_without_saving(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    coding: str,
    wire: bytes,
    error: type[Exception],
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire, body=BODY)
    with pytest.raises(error):
        fetch_upstream.main()
    assert list(destination.iterdir()) == []


@pytest.mark.parametrize(
    "cut",
    [
        pytest.param(1, id="partial-header"),
        pytest.param(len(BROTLI) // 2, id="partial-payload"),
        pytest.param(-1, id="missing-final-marker"),
    ],
)
@pytest.mark.parametrize("outer_layer", [False, True])
def test_fetch_rejects_incomplete_brotli_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, cut: int, outer_layer: bool
) -> None:
    coding, wire = "br", BROTLI[:cut]
    if outer_layer:
        coding, wire = "br, gzip", gzip.compress(wire, mtime=0)
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire, body=BODY)
    with pytest.raises(brotli.error):
        fetch_upstream.main()
    assert list(destination.iterdir()) == []
