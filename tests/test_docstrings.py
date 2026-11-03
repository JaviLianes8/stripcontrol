"""Run public docstrings and the guide as consumers of the public package."""

from __future__ import annotations

import doctest
import importlib
import inspect
import re
from pathlib import Path

import pytest

import stripcontrol


@pytest.mark.parametrize(
    "module",
    ["stripcontrol", "stripcontrol._control", "stripcontrol._bytes", "stripcontrol._stripper"],
)
def test_docstrings_execute(module: str) -> None:
    result = doctest.testmod(importlib.import_module(module))
    assert result.failed == 0
    assert result.attempted > 0


def test_every_public_callable_has_a_runnable_example() -> None:
    for name in stripcontrol.__all__:
        value = getattr(stripcontrol, name)
        if callable(value):
            assert ">>>" in (inspect.getdoc(value) or ""), name
    for name in ["feed", "close", "in_sequence"]:
        assert ">>>" in (inspect.getdoc(getattr(stripcontrol.ControlStripper, name)) or "")


def test_guide_python_examples_run() -> None:
    path = Path(__file__).resolve().parents[1] / "GUIDE.md"
    blocks = re.findall(r"```python\n(.*?)```", path.read_text(encoding="utf-8"), re.DOTALL)
    assert blocks
    for block in blocks:
        exec(compile(block, "GUIDE.md", "exec"), {})
