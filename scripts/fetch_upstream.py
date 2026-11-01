"""Fetch the third-party test files listed in tests/upstream/MANIFEST.json.

The files are not part of the repository. Their tests skip until this script has fetched
them; each download is checked against the size and sha256 in the manifest.

    python scripts/fetch_upstream.py
"""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import sys
import urllib.request
import zlib
from pathlib import Path
from typing import cast

import brotli  # type: ignore[import-untyped]

FOLDER = Path(__file__).resolve().parents[1] / "tests" / "upstream"


def _decode(body: bytes, encoding: str) -> bytes:
    for coding in reversed(encoding.lower().split(",")):
        coding = coding.strip()
        if coding == "br":
            body = cast(bytes, brotli.decompress(body))
        elif coding == "gzip":
            body = gzip.decompress(body)
        elif coding == "deflate":
            body = zlib.decompress(body)
        elif coding not in ("", "identity"):
            raise ValueError("unsupported HTTP content encoding")
    return body


def main() -> int:
    manifest = json.loads((FOLDER / "MANIFEST.json").read_text(encoding="utf-8"))
    destination = Path(os.environ.get("STRIPCONTROL_UPSTREAM", str(FOLDER)))
    destination.mkdir(parents=True, exist_ok=True)
    failed = 0
    for name, entry in manifest.items():
        with urllib.request.urlopen(entry["url"], timeout=60) as response:
            body = _decode(response.read(), response.headers.get("Content-Encoding", ""))
        digest = hashlib.sha256(body).hexdigest()
        if len(body) != entry["size"] or digest != entry["sha256"]:
            print(f"{name}: got {len(body)} bytes, sha256 {digest}; manifest differs")
            failed += 1
            continue
        (destination / name).write_bytes(body)
        print(f"{name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
