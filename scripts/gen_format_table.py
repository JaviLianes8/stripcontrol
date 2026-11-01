"""Regenerate src/stripcontrol/_format_table.py from the pinned Unicode category file.

Run `python scripts/fetch_upstream.py` first, then:

    python scripts/gen_format_table.py

Only the code point ranges are written out; no text from the source file is copied.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "tests" / "upstream"
SOURCE = (
    Path(os.environ.get("STRIPCONTROL_UPSTREAM", str(FOLDER)))
    / "unicode-18-DerivedGeneralCategory.txt"
)
TARGET = ROOT / "src" / "stripcontrol" / "_format_table.py"
_LINE = re.compile(r"^([0-9A-F]{4,6})(?:\.\.([0-9A-F]{4,6}))?\s*;\s*(\w+)")


def category_ranges(text: str, category: str) -> list[tuple[int, int]]:
    """Return the sorted, merged ranges of one general category in a UCD extracted file."""
    ranges: list[tuple[int, int]] = []
    for line in text.splitlines():
        match = _LINE.match(line)
        if match is None or match.group(3) != category:
            continue
        start = int(match.group(1), 16)
        end = int(match.group(2) or match.group(1), 16)
        if ranges and ranges[-1][1] + 1 == start:
            ranges[-1] = (ranges[-1][0], end)
        else:
            ranges.append((start, end))
    return sorted(ranges)


def render(ranges: list[tuple[int, int]], revision: str) -> str:
    rows = "\n".join(f"    (0x{start:04X}, 0x{end:04X})," for start, end in ranges)
    return (
        '"""Unicode format characters (general category Cf), generated; do not edit."""\n\n'
        "from __future__ import annotations\n\n"
        f'UNICODE_VERSION = "{revision}"\n\n'
        "# Inclusive code point ranges, from scripts/gen_format_table.py.\n"
        f"FORMAT_RANGES: tuple[tuple[int, int], ...] = (\n{rows}\n)\n"
    )


def main() -> int:
    manifest = json.loads((FOLDER / "MANIFEST.json").read_text(encoding="utf-8"))
    revision = manifest[SOURCE.name]["revision"].removeprefix("Unicode ")
    ranges = category_ranges(SOURCE.read_text(encoding="utf-8"), "Cf")
    TARGET.write_text(render(ranges, revision), encoding="utf-8", newline="\n")
    print(f"{TARGET.name}: {len(ranges)} ranges, Unicode {revision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
