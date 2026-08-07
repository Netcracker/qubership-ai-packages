#!/usr/bin/env python3
"""Edge cases for the Go half of the comment-only oracle.

Run with `python3 test_strip_go_comments.py`. Every case here is one a regex or a line-oriented
stripper gets wrong, plus the behaviours the sweep depends on: deleting a comment is invisible,
rewrapping code is not, and an unterminated literal is an error rather than a silent pass.

The raw string literal carries most of the weight. It spans lines, has no escapes, and swallows
`//`, `/*`, and a lone double quote — so a stripper that is right about Java strings is still wrong
about Go.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from strip_go_comments import (  # noqa: E402
    ParseError,
    resolve_under_root,
    first_difference,
    normalize,
    scan,
)

FAILURES: list[str] = []


def check(name: str, actual, expected) -> None:
    if actual != expected:
        FAILURES.append(f"{name}\n      expected: {expected!r}\n      actual:   {actual!r}")


def raises(name: str, exc_type, thunk) -> None:
    try:
        thunk()
    except exc_type:
        return
    except Exception as exc:  # noqa: BLE001
        FAILURES.append(f"{name}\n      raised {type(exc).__name__} instead of {exc_type.__name__}")
        return
    FAILURES.append(f"{name}\n      raised nothing; expected {exc_type.__name__}")


def kinds(src: str) -> list[str]:
    return [s.kind for s in scan(src)]


def texts(src: str) -> list[str]:
    return [s.text for s in scan(src)]


def code(src: str) -> list[str]:
    return normalize(src).lines


# ---------------------------------------------------------------- the ordinary cases

check("line comment", kinds("package p\n// hello\n"), ["line"])
check("block comment", kinds("package p\n/* hello */\n"), ["block"])
check("no doc kind is ever reported", kinds("// Foo does it.\nfunc Foo() {}\n"), ["line"])
check(
    "trailing comment after code",
    texts('x := 1 // why\n'),
    ["// why"],
)
check("comment at EOF without a newline", texts("x := 1 // end"), ["// end"])
check("empty line comment", kinds("//\n"), ["line"])
check("block comment spanning lines", kinds("/*\n a\n b\n*/\n"), ["block"])
check("*/ inside a line comment does not close anything", kinds("// */ still a comment\n"), ["line"])
check("block comments do not nest", texts("/* a /* b */ c */"), ["/* a /* b */"])

# ---------------------------------------------------------------- literals are not comments

check("// inside an interpreted string", kinds('u := "http://example.com"\n'), [])
check("/* inside an interpreted string", kinds('s := "/* not a comment */"\n'), [])
check("escaped quote does not end the string", kinds('s := "he said \\"hi\\" // no"\n'), [])
check(
    "escaped backslash ends the string, so the comment after it is real",
    texts('s := "back\\\\" // yes\n'),
    ["// yes"],
)
check("rune literal holding a slash", kinds("c := '/'\n"), [])
check("escaped rune literal", kinds("c := '\\''\n// after\n"), ["line"])
check("rune literal holding a quote", kinds("c := '\"'\n"), [])

# ---------------------------------------------------------------- raw strings, the Go-specific trap

check("// inside a raw string", kinds("s := `http://example.com`\n"), [])
check("/* inside a raw string", kinds("s := `/* nope */`\n"), [])
check(
    "raw string spanning lines swallows everything",
    kinds("s := `\nline // not a comment\n/* nor this */\n`\n// real\n"),
    ["line"],
)
check("a double quote inside a raw string does not open a string", kinds('s := `a "b` // real\n'), ["line"])
check("a backslash in a raw string is not an escape", kinds("s := `a\\` // real\n"), ["line"])

# ---------------------------------------------------------------- errors, not silent passes

raises("unterminated block comment", ParseError, lambda: scan("/* forever\n"))
raises("unterminated raw string", ParseError, lambda: scan("s := `forever\n"))
raises("unterminated interpreted string", ParseError, lambda: scan('s := "forever\n'))
raises("unterminated rune literal", ParseError, lambda: scan("c := 'x\n"))

# ---------------------------------------------------------------- what the sweep depends on

BEFORE = """package p

// Old summary.
// Second line.
func F(a int) int {
\t/* a block
\t   over lines */
\treturn a + 1 // trailing
}
"""

COMMENTS_ONLY = """package p

// New summary, restructured and longer than the one it replaced.
func F(a int) int {
\treturn a + 1
}
"""

CODE_MOVED = """package p

// Old summary.
// Second line.
func F(a int) int {
\treturn a +
\t\t1
}
"""

check(
    "deleting and rewriting comments leaves the normalized form untouched",
    first_difference(BEFORE, COMMENTS_ONLY),
    None,
)
check(
    "rewrapping an expression across lines is a code change",
    first_difference(BEFORE, CODE_MOVED) is None,
    False,
)
check(
    "indentation alone is not a code change",
    first_difference("func F() {\n\treturn\n}\n", "func F() {\n        return\n}\n"),
    None,
)
check(
    "closing up a space between tokens is a code change",
    first_difference("x := a + b\n", "x := a+b\n") is None,
    False,
)
check(
    "a comment between tokens leaves the code on one line",
    code("x := a /* mid */ + b\n"),
    ["x := a + b"],
)

# ---------------------------------------------------------------- the CLI

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "t@t"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
    target = root / "f.go"
    target.write_text(BEFORE, encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "add", "f.go"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", "base"], check=True)

    target.write_text(COMMENTS_ONLY, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "strip_go_comments.py"),
         "verify", "--root", str(root), "--ref", "HEAD", "--files", "f.go"],
        capture_output=True,
        text=True,
    )
    check("verify exits 0 when only comments moved", proc.returncode, 0)

    target.write_text(CODE_MOVED, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "strip_go_comments.py"),
         "verify", "--root", str(root), "--ref", "HEAD", "--files", "f.go"],
        capture_output=True,
        text=True,
    )
    check("verify exits non-zero when code moved", proc.returncode != 0, True)

    # The gate agent may pass either form, and a run really did mix them: an absolute path used to
    # resolve to nothing and be reported as "new", indistinguishable from a file the branch adds.
    target.write_text(COMMENTS_ONLY, encoding="utf-8")

    def verify(*files):
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).parent / "strip_go_comments.py"),
             "verify", "--root", str(root), "--ref", "HEAD", "--files", *files],
            capture_output=True, text=True,
        )
        try:
            return json.loads(proc.stdout)["results"][0]["status"], proc.returncode
        except (ValueError, KeyError, IndexError):
            return f"no parsable result: {proc.stderr.strip()[:120]}", proc.returncode

    check("a relative path verifies", verify("f.go")[0], "pass")
    check("an absolute path verifies the same file", verify(str(target))[0], "pass")
    check("an absolute path does not exit non-zero", verify(str(target))[1], 0)
    missing, code = verify("nope.go")
    check("a path that is not on disk is missing, not new", missing, "missing")
    check("…and it fails the run", code != 0, True)
    outside, code = verify("/etc/hosts")
    check("a path outside the root is refused", outside, "outside-root")
    check("…and that fails the run too", code != 0, True)

check("resolve_under_root leaves a relative path alone", resolve_under_root("/a/b", "c/d.go"), "c/d.go")
check("resolve_under_root makes an absolute path relative", resolve_under_root("/a/b", "/a/b/c/d.go"), "c/d.go")
raises(
    "resolve_under_root refuses a path outside the root",
    ValueError,
    lambda: resolve_under_root("/a/b", "/x/y.go"),
)

# ---------------------------------------------------------------- report

if FAILURES:
    print(f"{len(FAILURES)} failed:\n")
    for f in FAILURES:
        print(f"  - {f}\n")
    sys.exit(1)
print("all cases pass")
