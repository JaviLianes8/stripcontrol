"""Handwritten HTTP bodies verify decoding before manifest validation and storage."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import sys
import urllib.request
import zlib
from email.message import Message
from pathlib import Path

import brotli  # type: ignore[import-untyped]
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import fetch_upstream as fetch_upstream

BODY = b"Handwritten reference content.\n" * 20
GZIP_MEMBERS = gzip.compress(BODY[:23], mtime=0) + gzip.compress(BODY[23:], mtime=0)


class _Response(io.BytesIO):
    def __init__(self, data: bytes, coding: str) -> None:
        super().__init__(data)
        self.headers = Message()
        if coding:
            self.headers["Content-Encoding"] = coding


def _prepare_fetch(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    coding: str,
    wire: bytes,
    valid: bool = True,
    *,
    body: bytes = BODY,
) -> Path:
    manifest = {
        "reference.txt": {
            "url": "https://example.test/reference",
            "size": len(body),
            "sha256": hashlib.sha256(body if valid else b"different").hexdigest(),
        }
    }
    (tmp_path / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    destination = tmp_path / "download"
    monkeypatch.setattr(fetch_upstream, "FOLDER", tmp_path)
    monkeypatch.setenv("STRIPCONTROL_UPSTREAM", str(destination))
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: _Response(wire, coding))
    return destination


@pytest.mark.parametrize(
    ("coding", "wire"),
    [
        ("", BODY),
        ("identity", BODY),
        ("br", brotli.compress(BODY)),
        ("gzip", gzip.compress(BODY)),
        ("deflate", zlib.compress(BODY)),
        ("gzip, br", brotli.compress(gzip.compress(BODY))),
        ("bR", brotli.compress(BODY)),
        ("GZip", gzip.compress(BODY)),
        ("DeFlAtE", zlib.compress(BODY)),
        ("GZip, DeFlAtE, bR", brotli.compress(zlib.compress(gzip.compress(BODY)))),
        ("identity, gzip", gzip.compress(BODY)),
        ("gzip, identity", gzip.compress(BODY)),
        ("identity, gzip, identity", gzip.compress(BODY)),
        ("gzip, identity, br", brotli.compress(gzip.compress(BODY))),
        ("IdEnTiTy, GZip, identity, bR, IdEnTiTy", brotli.compress(gzip.compress(BODY))),
        ("\tgzip\t", gzip.compress(BODY)),
        ("\tbr\t", brotli.compress(BODY)),
        ("\tdeflate\t", zlib.compress(BODY)),
        ("\tgzip\t,\tbr\t", brotli.compress(gzip.compress(BODY))),
        ("gzip ", gzip.compress(BODY)),
        ("br ", brotli.compress(BODY)),
        ("deflate ", zlib.compress(BODY)),
        ("gzip , br ", brotli.compress(gzip.compress(BODY))),
        ("gzip , deflate , br ", brotli.compress(zlib.compress(gzip.compress(BODY)))),
        (" \tGZip\t , \tbR \t", brotli.compress(gzip.compress(BODY))),
        ("gzip, gzip", gzip.compress(gzip.compress(BODY))),
        ("br, br", brotli.compress(brotli.compress(BODY))),
        ("deflate, deflate", zlib.compress(zlib.compress(BODY))),
        ("gzip, br, gzip", gzip.compress(brotli.compress(gzip.compress(BODY)))),
        ("deflate, gzip, deflate", zlib.compress(gzip.compress(zlib.compress(BODY)))),
        ("GZip , identity, \tgzip\t", gzip.compress(gzip.compress(BODY))),
        (", gzip", gzip.compress(BODY)),
        ("gzip, ", gzip.compress(BODY)),
        (", gzip, ", gzip.compress(BODY)),
        (", br, ", brotli.compress(BODY)),
        (", deflate, ", zlib.compress(BODY)),
        ("gzip,, br", brotli.compress(gzip.compress(BODY))),
        ("gzip, \t, br", brotli.compress(gzip.compress(BODY))),
        ("gzip, br, ", brotli.compress(gzip.compress(BODY))),
        (", gzip,, br,", brotli.compress(gzip.compress(BODY))),
        (" , identity, gzip, , ", gzip.compress(BODY)),
        (", , \t,", BODY),
        ("gzip", GZIP_MEMBERS),
        ("gzip, br", brotli.compress(GZIP_MEMBERS)),
        ("gzip", gzip.compress(b"", mtime=0) + GZIP_MEMBERS + gzip.compress(b"", mtime=0)),
    ],
)
@pytest.mark.parametrize("valid", [True, False])
def test_fetch_validates_and_saves_decoded_content(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, wire: bytes, valid: bool
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire, valid)
    assert fetch_upstream.main() == (0 if valid else 1)
    if valid:
        assert (destination / "reference.txt").read_bytes() == BODY
    else:
        assert not (destination / "reference.txt").exists()


@pytest.mark.parametrize(
    ("coding", "wire"),
    [
        ("unsupported-coding", BODY),
        ("gzip, unsupported-coding", gzip.compress(BODY)),
        ("unsupported-coding, gzip", gzip.compress(BODY)),
        ("g zip", gzip.compress(BODY)),
        ("g\tzip", gzip.compress(BODY)),
        ("b r", brotli.compress(BODY)),
        ("b\tr", brotli.compress(BODY)),
        ("de flate", zlib.compress(BODY)),
        ("de\tflate", zlib.compress(BODY)),
        ("ident ity", BODY),
        ("ident\tity", BODY),
        ("gzip, b r", brotli.compress(gzip.compress(BODY))),
        ("g zip, br", brotli.compress(gzip.compress(BODY))),
        ("gzip;q=1", gzip.compress(BODY)),
        ("gzip; q=1", gzip.compress(BODY)),
        ("gzip;", gzip.compress(BODY)),
        ("br;q=1", brotli.compress(BODY)),
        ("deflate;q=1", zlib.compress(BODY)),
        ("identity;q=1", BODY),
        ("gzip, br;q=1", brotli.compress(gzip.compress(BODY))),
        ("gzip;q=1, br", brotli.compress(gzip.compress(BODY))),
    ],
)
def test_fetch_rejects_unsupported_encoding_without_saving(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, coding: str, wire: bytes
) -> None:
    destination = _prepare_fetch(monkeypatch, tmp_path, coding, wire)
    with pytest.raises(ValueError, match=r"^unsupported HTTP content encoding$"):
        fetch_upstream.main()
    assert list(destination.iterdir()) == []
