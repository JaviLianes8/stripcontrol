"""Bounded diagnostics for command line arguments and file names."""

from __future__ import annotations

import argparse
import re
from typing import NoReturn

from ._control import escape_char, escape_control

_SURROGATE = re.compile("[\ud800-\udfff]")


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # argparse includes complete argument values in many of its diagnostics.
        super().error("invalid arguments; see --help")


def shown(name: str) -> str:
    # Bound before escaping too, so hostile names cannot expand into large messages.
    text = escape_control(name[:120], keep="", format_chars=True)

    def surrogate(match: re.Match[str]) -> str:
        code = ord(match.group())
        return escape_char(code - 0xDC00 if code >= 0xDC80 else code)

    text = _SURROGATE.sub(surrogate, text)
    return text[:120] + ("..." if len(name) > 120 or len(text) > 120 else "")
