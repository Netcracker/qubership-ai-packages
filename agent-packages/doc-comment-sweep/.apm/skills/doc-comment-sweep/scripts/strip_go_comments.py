#!/usr/bin/env python3
"""Prove that an edit to Go source changed comments and nothing else.

The Go half of the sweep's comment-only oracle. It lexes Go well enough to know a comment from a
slash inside a string literal, removes the comments, and compares what is left — the same contract
`strip_java_comments.py` states, held to the same normalization, which this module imports rather
than reimplements.

Two subcommands:

  strip   print the normalized form of one file, for eyeballing what the comparison actually sees
  verify  compare each file against a git ref and exit non-zero when code moved

Go is a far easier language to lex than Java for this purpose, and the difference is worth naming
because it changes what the oracle can promise. Java has to refuse a file whose `\\uXXXX` escapes
could encode a quote or a slash, because the compiler resolves those before lexing; Go has no
pre-lex escape mechanism at all, so `Unverifiable` never happens here. What Go adds instead is the
raw string literal: backticks span lines, contain no escapes, and swallow `//` and `/*` whole.

`scan` reports `line` and `block` spans and never `doc`. That is not an omission. A Go doc comment
is a comment group sitting immediately above a declaration, which is a position, not a spelling —
nothing in the text of `// Foo does the thing.` distinguishes it from a comment inside a function.
The caller decides, in `sweep_targets.py`, where the declaration line numbers are known.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from strip_java_comments import (  # noqa: E402
    Diff,
    Normalized,
    ParseError,
    Span,
    _line_of,
    _line_starts,
    _read,
    verify_files,
    first_difference as _first_difference,
    normalize as _normalize,
)

# Span, ParseError and Unverifiable describe comments, not Java, and normalize() is the definition of
# "the code moved". Both languages import them from the module that happens to have been written
# first; when a third language lands, move them to a neutral module rather than copying them.


def _scan(src: str, include_literals: bool) -> list[Span]:
    """Every comment in a Go source file, in source order.

    Raises ParseError on an unterminated string, rune, or block comment. Never raises Unverifiable:
    unlike Java, Go resolves no escape before lexing, so there is no construct this refuses to reason
    about.
    """
    starts = _line_starts(src)
    spans: list[Span] = []
    i, n = 0, len(src)

    while i < n:
        ch = src[i]

        if ch == "/" and i + 1 < n:
            nxt = src[i + 1]
            if nxt == "/":
                end = src.find("\n", i)
                if end == -1:
                    end = n
                spans.append(
                    Span("line", i, end, _line_of(starts, i), _line_of(starts, max(i, end - 1)), src[i:end])
                )
                i = end
                continue
            if nxt == "*":
                end = src.find("*/", i + 2)
                if end == -1:
                    raise ParseError(f"unterminated block comment at line {_line_of(starts, i)}")
                end += 2
                spans.append(
                    Span("block", i, end, _line_of(starts, i), _line_of(starts, end - 1), src[i:end])
                )
                i = end
                continue

        if ch == "`":
            # Raw string literal: no escapes, runs across lines, and anything inside it — including
            # //, /*, and a lone " — is data. This is the one construct that makes a naive
            # line-oriented comment stripper wrong on Go.
            literal_start = i
            end = src.find("`", i + 1)
            if end == -1:
                raise ParseError(f"unterminated raw string literal at line {_line_of(starts, i)}")
            i = end + 1
            if include_literals:
                spans.append(
                    Span("literal", literal_start, i, _line_of(starts, literal_start),
                         _line_of(starts, i - 1), src[literal_start:i])
                )
            continue

        if ch in ('"', "'"):
            kind = "string" if ch == '"' else "rune"
            literal_start = i
            i += 1
            while True:
                if i >= n or src[i] == "\n":
                    raise ParseError(f"unterminated {kind} literal at line {_line_of(starts, i - 1)}")
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == ch:
                    i += 1
                    break
                i += 1
            if include_literals:
                spans.append(
                    Span("literal", literal_start, i, _line_of(starts, literal_start),
                         _line_of(starts, i - 1), src[literal_start:i])
                )
            continue

        i += 1

    return spans


def scan(src: str) -> list[Span]:
    """Every comment in a Go source file, in source order."""
    return _scan(src, False)


def scan_literals(src: str) -> list[Span]:
    """Literal spans whose contents must remain byte-for-byte significant."""
    return [span for span in _scan(src, True) if span.kind == "literal"]


def normalize(src: str) -> Normalized:
    """The comment-free, whitespace-collapsed form of a Go file."""
    return _normalize(src, scan, scan_literals)


def first_difference(before: str, after: str) -> Diff | None:
    """The first code line that differs between two revisions, or None when only comments moved."""
    return _first_difference(before, after, scan, scan_literals)


def cmd_strip(args: argparse.Namespace) -> int:
    out = normalize(_read(args.file))
    for line_no, text in zip(out.source_lines, out.lines):
        print(f"{line_no:6d}  {text}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    return verify_files(args, first_difference)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_strip = sub.add_parser("strip", help="print the normalized form of one file")
    p_strip.add_argument("file")
    p_strip.set_defaults(func=cmd_strip)

    p_verify = sub.add_parser("verify", help="compare files against a git ref")
    p_verify.add_argument("--root", required=True)
    p_verify.add_argument("--ref", required=True)
    p_verify.add_argument("--files", nargs="+", required=True)
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
