"""The stripcontrol command line: strip, escape or report control characters in files."""

from __future__ import annotations

import argparse
import codecs
import errno
import os
import sys
from collections.abc import Callable, Iterator, Sequence
from typing import BinaryIO

from ._bytes import ERRORS, STRAY_C1, Encoding
from ._control import STANDARD_WHITESPACE, escape_char, escape_control, find_control
from ._stripper import ControlStripper

_CHUNK = 1 << 16


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stripcontrol",
        description="Copy FILEs (or stdin) to stdout without control characters and "
        "terminal escape sequences.",
    )
    parser.add_argument("files", nargs="*", metavar="FILE", help="files to read; - is stdin")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="print FILE:LINE:COLUMN of each control character, exit 1 if any",
    )
    mode.add_argument("--escape", action="store_true", help="write controls as \\xNN escapes")
    parser.add_argument(
        "--chars-only", action="store_true", help="remove control characters, not sequences"
    )
    parser.add_argument(
        "--format-chars", action="store_true", help="also act on Unicode format characters (Cf)"
    )
    parser.add_argument(
        "--strip-whitespace", action="store_true", help="do not keep tab, newline and return"
    )
    parser.add_argument(
        "--latin-1", action="store_true", help="read bytes 80..9F as 8-bit C1, not UTF-8"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line with argv (default: sys.argv[1:]) and return the exit code."""
    args = _parser().parse_args(argv)
    codec: Encoding = "latin-1" if args.latin_1 else "utf-8"
    keep = "" if args.strip_whitespace else STANDARD_WHITESPACE
    status = 0
    try:
        for name in args.files or ["-"]:
            try:
                with _open(name) as stream:
                    chunks = _decode(stream, codec)
                    if args.check:
                        if _check(name, chunks, keep, args.format_chars):
                            status = max(status, 1)
                        continue
                    out: Iterator[str]
                    if args.escape:
                        out = (_escape(chunk, keep, args.format_chars) for chunk in chunks)
                    else:
                        out = _strip(chunks, keep, not args.chars_only, args.format_chars, codec)
                    for piece in out:
                        _write(piece.encode(codec, ERRORS))
            except OSError as error:
                if name == "-" or error.filename is None:
                    raise
                print(f"stripcontrol: {name}: {error.strerror}", file=sys.stderr)
                status = 2
    except OSError as error:
        # The reader went away (`stripcontrol log | head`); Windows reports it as EINVAL.
        if not isinstance(error, BrokenPipeError) and error.errno != errno.EINVAL:
            raise
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return status


def _open(name: str) -> BinaryIO:
    if name == "-":
        return os.fdopen(os.dup(sys.stdin.fileno()), "rb")
    return open(name, "rb")  # closed by the caller's with block


def _decode(stream: BinaryIO, codec: Encoding) -> Iterator[str]:
    decoder = codecs.getincrementaldecoder(codec)(ERRORS)
    read: Callable[[int], bytes] = getattr(stream, "read1", stream.read)
    while data := read(_CHUNK):
        yield decoder.decode(data)
    yield decoder.decode(b"", final=True)


def _strip(
    chunks: Iterator[str], keep: str, sequences: bool, format_chars: bool, codec: Encoding
) -> Iterator[str]:
    stripper = ControlStripper(keep=keep, sequences=sequences, format_chars=format_chars)
    for chunk in chunks:
        yield stripper.feed(STRAY_C1.sub("", chunk) if codec == "utf-8" else chunk)
    yield stripper.close()


def _escape(chunk: str, keep: str, format_chars: bool) -> str:
    shown = escape_control(chunk, keep=keep, format_chars=format_chars)
    return STRAY_C1.sub(lambda match: escape_char(ord(match.group()) - 0xDC00), shown)


def _check(name: str, chunks: Iterator[str], keep: str, format_chars: bool) -> bool:
    found, line, column = False, 1, 1
    for chunk in chunks:
        hits = find_control(chunk, keep=keep, format_chars=format_chars)
        hits += [(match.start(), ord(match.group()) - 0xDC00) for match in STRAY_C1.finditer(chunk)]
        start = 0
        for index, code in sorted(hits):
            line, column = _advance(chunk, start, index, line, column)
            start = index
            stray = "\udc80" <= chunk[index] <= "\udc9f"
            label = f"byte 0x{code:02x}" if stray else f"U+{code:04X}"
            _write(f"{name}:{line}:{column}: {label}\n".encode("utf-8", ERRORS))
            found = True
        line, column = _advance(chunk, start, len(chunk), line, column)
    return found


def _advance(text: str, start: int, stop: int, line: int, column: int) -> tuple[int, int]:
    newlines = text.count("\n", start, stop)
    if newlines:
        return line + newlines, stop - text.rindex("\n", start, stop)
    return line, column + stop - start


def _write(data: bytes) -> None:
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
