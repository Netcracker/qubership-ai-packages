#!/usr/bin/env python3
"""Edge cases for the comment-only oracle.

Run with `python3 test_strip_java_comments.py`. Every case here is one the naive implementation --
regex, or a lexer without literal states -- gets wrong, plus the four behaviours the sweep depends
on: deleting a comment is invisible, rewrapping code is not, a pre-lex unicode escape is refused
rather than guessed, and an unterminated literal is an error rather than a silent pass.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from strip_java_comments import (  # noqa: E402
    ParseError,
    Unverifiable,
    first_difference,
    normalize,
    scan,
)

FAILURES: list[str] = []


def check(name: str, actual, expected) -> None:
    if actual != expected:
        FAILURES.append(f"{name}\n     expected: {expected!r}\n     actual:   {actual!r}")


def raises(name: str, exc_type, thunk) -> None:
    try:
        thunk()
    except exc_type:
        return
    except Exception as exc:  # noqa: BLE001 - the point is that the wrong exception is a failure
        FAILURES.append(f"{name}\n     expected {exc_type.__name__}, got {type(exc).__name__}: {exc}")
        return
    FAILURES.append(f"{name}\n     expected {exc_type.__name__}, nothing raised")


def kinds(src: str) -> list[str]:
    return [s.kind for s in scan(src)]


def texts(src: str) -> list[str]:
    return [s.text for s in scan(src)]


# ---------------------------------------------------------------- the lexer

check("// inside a string literal is not a comment", kinds('String u = "http://x";'), [])
check("/* inside a string literal is not a comment", kinds('String s = "/*";'), [])
check("a quote inside a char literal", kinds("""char q = '"'; // real"""), ["line"])
check("an escaped quote inside a char literal", kinds(r"""char q = '\''; // real"""), ["line"])
check("an escaped quote inside a string literal", kinds(r'''String s = "a\"b"; // real'''), ["line"])
check("a backslash before the closing quote", kinds(r'String s = "a\\"; // real'), ["line"])

check("block comments do not nest", texts("/* /* */ code"), ["/* /* */"])
check("an empty block comment is not javadoc", kinds("/**/ code"), ["block"])
check("a doc comment is tagged doc", kinds("/** hi */ code"), ["doc"])
check("a line comment with no trailing newline", texts("code // tail"), ["// tail"])
check("a line comment ends at the newline", texts("// a\ncode"), ["// a"])

check("four quotes are two empty strings, not a text block", kinds('String s = """"; // real'), ["line"])
check(
    "a text block opener needs a line terminator",
    kinds('String s = """\nbody\n"""; // real'),
    ["line"],
)
check(
    "an escaped triple quote does not close a text block",
    kinds('String s = """\na\\"""b\n"""; // real'),
    ["line"],
)
check(
    "a lone quote inside a text block",
    kinds('String s = """\nsay "hi"\n"""; // real'),
    ["line"],
)
check(
    "// inside a text block is not a comment",
    kinds('String s = """\nhttp://x\n""";'),
    [],
)

raises("an unterminated block comment is an error", ParseError, lambda: scan("code /* open"))
raises("an unterminated string is an error", ParseError, lambda: scan('String s = "open;'))
raises("a newline inside a string is an error", ParseError, lambda: scan('String s = "a\nb";'))
def java_escape(body: str) -> str:
    """Spell a Java unicode escape without writing one.

    A literal backslash-u in this file would be decoded by the editor, the shell, or Python itself
    long before the lexer sees it, and the case under test would silently become ordinary text.
    """
    return chr(92) + body


raises("a slash spelled as a unicode escape is refused", Unverifiable,
       lambda: scan("int x = 1; " + java_escape("u002f") + java_escape("u002f") + " no"))
raises("a quote spelled as a unicode escape is refused", Unverifiable,
       lambda: scan("String s = " + java_escape("u0022") + "x" + java_escape("u0022") + ";"))
raises("a doubled-u escape is refused too", Unverifiable,
       lambda: scan("int x; " + java_escape("uuuu002f") + java_escape("uuuu002f") + " no"))
check("a backslash that is itself escaped does not make an escape",
      kinds('String s = "a' + chr(92) * 2 + 'u002f"; // real'), ["line"])

# ---------------------------------------------------------------- normalization

check(
    "indentation is not a difference",
    first_difference("class A {\n  int x;\n}\n", "class A {\n        int x;\n}\n"),
    None,
)
check(
    "deleting a whole-line comment is not a difference",
    first_difference("int a;\n// note\nint b;\n", "int a;\nint b;\n"),
    None,
)
check(
    "deleting a trailing comment is not a difference",
    first_difference("int a; // note\n", "int a;\n"),
    None,
)
check(
    "deleting a block comment that spanned lines mid-expression is not a difference",
    first_difference("int x = /* a\nb */ 1;\n", "int x = 1;\n"),
    None,
)
check(
    "adding a multi-line javadoc is not a difference",
    first_difference("int f() { return 1; }\n", "/**\n * Returns one.\n *\n * @return one\n */\nint f() { return 1; }\n"),
    None,
)
check(
    "rewriting a javadoc body is not a difference",
    first_difference("/** Old. */\nint f();\n", "/**\n * New, and longer.\n */\nint f();\n"),
    None,
)

reflow = first_difference("foo(a, b);\n", "foo(a,\n    b);\n")
check("rewrapping a statement is a difference", reflow is not None, True)

swapped = first_difference('log("a");\n', 'log("b");\n')
check("a changed string literal is a difference", swapped is not None, True)
check("the report names the after-version line", swapped.line if swapped else None, 1)

renamed = first_difference("int count;\nint f() { return count; }\n", "int total;\nint f() { return total; }\n")
check("a rename is a difference", renamed is not None, True)
check("the report points at the first changed line", renamed.line if renamed else None, 1)

check(
    "a comment turning into code is a difference",
    first_difference("// int x = 1;\n", "int x = 1;\n") is not None,
    True,
)
check(
    "horizontal spacing inside a line is not a difference",
    first_difference("int  x   =  1;\n", "int x = 1;\n"),
    None,
)
# Leading whitespace is ignored so that realigning a member under a taller javadoc stays invisible,
# but spacing between tokens is not: the sweep has no business closing up a space inside a statement.
check(
    "closing up a space between tokens is a difference",
    first_difference("int x = 1;\n", "int x =1;\n") is not None,
    True,
)

check(
    "the normalized form drops comments and blank lines",
    normalize("/** doc */\nclass A {\n\n  // note\n  int x; // tail\n}\n").lines,
    ["class A {", "int x;", "}"],
)

# ---------------------------------------------------------------- verify, end to end

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    run = lambda *a: subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=True)
    run("init", "-q")
    run("config", "user.email", "t@t")
    run("config", "user.name", "t")

    (root / "A.java").write_text('class A {\n  /** Old. */\n  void f() { log("x"); }\n}\n')
    (root / "B.java").write_text("class B {\n  void g() {}\n}\n")
    run("add", "-A")
    run("commit", "-qm", "base")

    # A: comments only. B: a real code edit. C: added by the sweep, so it has no before-version.
    (root / "A.java").write_text('class A {\n  /**\n   * New wording, two lines.\n   */\n  void f() { log("x"); }\n}\n')
    (root / "B.java").write_text("class B {\n  void h() {}\n}\n")
    (root / "C.java").write_text("class C {}\n")

    script = str(Path(__file__).parent / "strip_java_comments.py")
    proc = subprocess.run(
        [sys.executable, script, "verify", "--root", str(root), "--ref", "HEAD",
         "--files", "A.java", "B.java", "C.java"],
        capture_output=True,
        text=True,
    )
    check("verify exits 1 when any file changed code", proc.returncode, 1)

    import json

    report = json.loads(proc.stdout)
    by_file = {f["file"]: f for f in report["files"]}
    check("verify reports the overall verdict", report["verdict"], "fail")
    check("a comment-only rewrite passes", by_file["A.java"]["status"], "pass")
    check("a code edit fails", by_file["B.java"]["status"], "fail")
    check("a file the branch added is not judged", by_file["C.java"]["status"], "new")
    check("the failure names a line", by_file["B.java"]["line"], 2)

    (root / "B.java").write_text("class B {\n  void g() {}\n}\n")
    proc = subprocess.run(
        [sys.executable, script, "verify", "--root", str(root), "--ref", "HEAD", "--files", "A.java", "B.java"],
        capture_output=True,
        text=True,
    )
    check("verify exits 0 when only comments moved", proc.returncode, 0)

# ---------------------------------------------------------------- report

if FAILURES:
    print(f"{len(FAILURES)} failed:\n")
    for f in FAILURES:
        print(f"  - {f}\n")
    sys.exit(1)
print("all cases pass")
