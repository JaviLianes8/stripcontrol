"""Check-report filenames use UTF-8 regardless of the input encoding."""

from __future__ import annotations

from pathlib import Path

import pytest
from test_cli import _run


@pytest.mark.parametrize("name", ["\u00e9.log", "\u65e5.log"])
@pytest.mark.parametrize("options", [[], ["--latin-1"]])
def test_check_reports_encode_file_labels_as_utf8(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, name: str, options: list[str]
) -> None:
    (tmp_path / name).write_bytes(b"x\x00")
    monkeypatch.chdir(tmp_path)
    code, output = _run(monkeypatch, ["--check", *options, name])
    assert code == 1
    assert output == name.encode("utf-8") + b":1:2: U+0000\n"
