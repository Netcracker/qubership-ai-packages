#!/usr/bin/env python3
"""Behaviour of the target survey, over a throwaway git repository.

Run with `python3 test_sweep_targets.py`. It builds a two-language repository in a temp directory,
commits it, edits it, and drives the real CLI — because every interesting decision here is made from
a git diff and an `sb map` call, and a unit test with hand-built inputs would assert the mock.

What it pins down, in order: which files the two scopes select, that `unchanged` exists in the
path-scoped scope and nowhere else, that a Go doc comment is not also collected as an inline comment,
that the filters for machine-read text hold, and that a file the scanner cannot read degrades instead
of failing the run.

Requires the `sb` binary on PATH. Without it the survey has no declarations to intersect and the
suite says so rather than reporting green.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sweep_targets import (  # noqa: E402
    _GROUP_DECL,
    LANGUAGES,
    attach_package_doc,
    git,
    language_for,
    scan_java,
)

SCRIPT = str(Path(__file__).parent / "sweep_targets.py")
FAILURES: list[str] = []


def check(name: str, actual, expected) -> None:
    if actual != expected:
        FAILURES.append(f"{name}\n      expected: {expected!r}\n      actual:   {actual!r}")


def check_true(name: str, actual) -> None:
    check(name, bool(actual), True)


# ---------------------------------------------------------------- the fixture

GO_TYPES = '''// Package api provides widget fixtures.
package api

// Colors are the palette the renderer accepts.
const (
	// Red is the default.
	Red  = "red"
	Blue = "blue"
)

// Widget is a thing with fields.
type Widget struct {
	// Name is what the thing is called.
	Name string `json:"name"`

	// +kubebuilder:validation:Required
	Size int `json:"size"`

	// Weight is documented, and its group ends in markers.
	// +kubebuilder:validation:Minimum=0
	// +optional
	Weight int `json:"weight,omitempty"`

	// +optional
	Note string `json:"note,omitempty"`
}

// Build assembles a Widget.
func Build(name string) *Widget {
	// The zero size is deliberate: callers set it afterwards.
	w := &Widget{Name: name}
	var (
		// A grouped declaration inside a function is not a doc comment.
		scratch int
	)
	_ = scratch
	// TODO: reject an empty name
	return w
}

//nolint:gocyclo
func Complicated() {}

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status

// Gadget is the Schema for gadgets.
type Gadget struct{}
'''

GO_UNTOUCHED = '''package api

// Untouched has never been edited on this branch.
func Untouched() {}
'''

GO_LICENSE = '''/*
Copyright 2026 Example Corp.
https://www.apache.org/licenses/LICENSE-2.0
*/
package api

func Licensed() {}
'''

GO_TEST = '''package api

// A widget must keep the name it was built with.
func TestBuild(t *testing.T) {}
'''

JAVA = """package p;

public class A {
    /** Returns the answer. */
    public int answer() {
        // why forty-two
        // Copy the array so the caller cannot mutate our state.
        int first = 1;
        // Copy the array so the caller never sees the update.
        return 42;
    }

    /** Returns the text length. */
    public int answer(String text) {
        return text.length();
    }

    /** Returns the supplied answer. */
    public int answer(int value) {
        return value;
    }
}
"""

JAVA_EDITED = JAVA.replace(
    """    /** Returns the text length. */
    public int answer(String text) {
        return text.length();
    }

""",
    "",
).replace("int answer(int value)", "int answer(int input)").replace("return value;", "return input;")

JAVA_DELETIONS = """package p;

public class DeleteMe {
    /** Returns one. */
    public int value() {
        // The constant is part of the wire contract.
        return 1;
    }
}
"""

JAVA_DELETIONS_EDITED = """package p;

public class DeleteMe {
    public int value() {
        return 1;
    }
}
"""

JAVA_PACKAGE = """/** Provides the p fixtures. */
package p;
"""

JAVA_PACKAGE_EDITED = """/** Provides fixture APIs in package p. */
package p;
"""

JAVA_LICENSE = """/*
 * Copyright 2026 Example Corp.
 * https://www.apache.org/licenses/LICENSE-2.0
 */
package p;

public class Licensed {}
"""


def run(root, *args, expect_ok=True):
    proc = subprocess.run(
        [sys.executable, SCRIPT, *args], capture_output=True, text=True, cwd=root
    )
    if expect_ok and proc.returncode != 0:
        raise RuntimeError(
            f"CLI failed ({proc.returncode}): {' '.join(args)}\n{proc.stderr.strip()}"
        )
    return proc


def survey(root, out, *extra):
    run(root, "survey", "--root", root, "--base", "HEAD", "--out", out, *extra)
    return json.loads(Path(out).read_text())


def targets_of(payload, path):
    """The file's report, or an empty one.

    Never None: a broken implementation has to surface as a named failing case, and indexing None
    ends the run in a traceback that says nothing about which behaviour broke.
    """
    for f in payload["files"]:
        if f["path"] == path:
            return f
    return {"path": path, "targets": [], "isTest": None, "degraded": None, "skippedComments": []}


def classes(payload):
    return {t.get("class", "inline") for f in payload["files"] for t in f["targets"]}


def inline_texts(payload, path):
    f = targets_of(payload, path)
    return [t["text"] for t in (f["targets"] if f else []) if t["kind"] == "inline"]


# ---------------------------------------------------------------- pure helpers, no repo needed

check("java suffix", language_for("a/B.java").name, "java")
check("go suffix", language_for("a/b.go").name, "go")
check("unknown suffix", language_for("a/b.py"), None)
check("go doc comments are positional", language_for("x.go").docs_by_position, True)
check("java doc comments are lexical", language_for("X.java").docs_by_position, False)
check("go test file", language_for("a/b_test.go").is_test("a/b_test.go"), True)
check("go non-test file", language_for("a/b.go").is_test("a/b.go"), False)
check("java test by name", language_for("FooTest.java").is_test("FooTest.java"), True)
check("java test by path", language_for("x.java").is_test("src/test/java/x.java"), True)
check("registry covers both languages", sorted(l.name for l in LANGUAGES), ["go", "java"])

java_license_decls = []
java_license_skip = attach_package_doc(
    java_license_decls, scan_java(JAVA_LICENSE), JAVA_LICENSE, "java/Licensed.java", language_for("X.java")
)
check("a regular Java file has no package-doc declaration", java_license_decls, [])
check_true("a regular Java package-adjacent comment has a skip reason", java_license_skip)

check_true("group decl at column 0", _GROUP_DECL.match("const ("))
check_true("var group at column 0", _GROUP_DECL.match("var ("))
check("indented group is not package level", _GROUP_DECL.match("\tvar ("), None)
check("an identifier starting with const is not a group", _GROUP_DECL.match("constant := 1"), None)

if not shutil.which("sb"):
    print("sb is not on PATH; the survey cases cannot run")
    sys.exit(1)

# ---------------------------------------------------------------- the repository

with tempfile.TemporaryDirectory() as tmp:
    root = str(Path(tmp).resolve())

    def write(rel, text):
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    write("go/api/types.go", GO_TYPES)
    write("go/api/untouched.go", GO_UNTOUCHED)
    write("go/api/licensed.go", GO_LICENSE)
    write("go/api/widget_test.go", GO_TEST)
    write("java/A.java", JAVA)
    write("java/Licensed.java", JAVA_LICENSE)
    write("java/DeleteMe.java", JAVA_DELETIONS)
    write("java/package-info.java", JAVA_PACKAGE)
    write("notes.md", "# not source\n")

    for cmd in (
        ["init", "-q", "-b", "main"],
        ["config", "user.email", "t@t"],
        ["config", "user.name", "t"],
        ["add", "-A"],
        ["commit", "-qm", "base"],
    ):
        subprocess.run(["git", "-C", root, *cmd], check=True, capture_output=True)

    # The branch edits one comment and one body in types.go, and deletes comments in DeleteMe.java.
    edited = GO_TYPES.replace(
        "// Build assembles a Widget.", "// Build assembles a Widget from a name."
    ).replace("w := &Widget{Name: name}", "w := &Widget{Name: name, Size: 0}")
    write("go/api/types.go", edited)
    # Touched too, so the exclusion path is exercised: a file only reaches `excluded` when the diff
    # offers it and no scanner claims the suffix.
    write("notes.md", "# not source, and edited\n")
    write("java/DeleteMe.java", JAVA_DELETIONS_EDITED)
    write("java/A.java", JAVA_EDITED)
    write("java/package-info.java", JAVA_PACKAGE_EDITED)

    out = str(Path(root) / "t.json")

    # ------------------------------------------------------------ scope: diff

    diff_payload = survey(root, out)
    diff_paths = sorted(f["path"] for f in diff_payload["files"])
    check(
        "diff scope selects the edited and comment-deletion files",
        diff_paths,
        ["go/api/types.go", "java/A.java", "java/DeleteMe.java", "java/package-info.java"],
    )
    check(
        "a file with no scanner is excluded, and the reason names the suffixes",
        any(e["path"] == "notes.md" and ".go" in e["reason"] for e in diff_payload["excluded"]),
        True,
    )
    check("diff scope never yields an unchanged target", "unchanged" in classes(diff_payload), False)

    doc_ids = {
        t["qualifiedName"]
        for f in diff_payload["files"]
        for t in f["targets"]
        if t["kind"] == "doc"
    }
    check_true("the edited declaration is a target", any("Build" in q for q in doc_ids))
    check(
        "a declaration the branch did not touch is not a target in diff scope",
        any("Complicated" in q for q in doc_ids),
        False,
    )

    # ------------------------------------------------------------ scope: path

    path_payload = survey(root, out, "--paths", "go/api")
    path_paths = sorted(f["path"] for f in path_payload["files"])
    check(
        "path scope selects every tracked file under the pathspec",
        path_paths,
        ["go/api/licensed.go", "go/api/types.go", "go/api/untouched.go", "go/api/widget_test.go"],
    )
    check("path scope records the pathspec it ran with", path_payload["pathspecs"], ["go/api"])
    check_true("path scope yields unchanged targets", "unchanged" in classes(path_payload))
    untouched = targets_of(path_payload, "go/api/untouched.go")
    check_true("an untouched file gets targets in path scope", untouched["targets"])
    check(
        "the untouched declaration is classified unchanged",
        {t.get("class") for t in untouched["targets"] if t["kind"] == "doc"},
        {"unchanged"},
    )
    check(
        "path scope marks the test file as a test",
        targets_of(path_payload, "go/api/widget_test.go")["isTest"],
        True,
    )
    check(
        "every file reports the language that claimed it",
        {f.get("language") for f in path_payload["files"]},
        {"go"},
    )
    # The orchestrator reads the printed summary, not targets.json, so a field only present in the
    # file is a field it never sees — which is how a Go batch got routed to the Java oracle.
    printed = json.loads(
        run(root, "survey", "--root", root, "--base", "HEAD", "--out", out, "--paths", "go/api").stdout
    )
    check(
        "the printed summary carries the language too, not just targets.json",
        {f.get("language") for f in printed["files"]},
        {"go"},
    )

    both = run(
        root, "survey", "--root", root, "--base", "HEAD", "--out", out,
        "--paths", "go/api", "--files", "go/api/types.go", expect_ok=False,
    )
    check("--paths and --files together are refused", both.returncode != 0, True)

    # ------------------------------------------------------------ Go doc comments are positional

    types_file = targets_of(path_payload, "go/api/types.go")
    check_true(
        "the Go package comment is a doc target",
        any(t.get("qualifiedName") == "api" for t in types_file["targets"]),
    )
    licensed_go = targets_of(path_payload, "go/api/licensed.go")
    check(
        "a Go license header is not a package doc target",
        any(t.get("declKind") == "package" for t in licensed_go["targets"]),
        False,
    )
    check_true(
        "a skipped Go license header is reported once",
        len(licensed_go["skippedComments"]) == 1,
    )
    inline = inline_texts(path_payload, "go/api/types.go")
    joined = "\n---\n".join(inline)
    check(
        "a doc comment above a func is not also an inline target",
        any("Build assembles" in t for t in inline),
        False,
    )
    check(
        "a doc comment above a package-level const group is not an inline target",
        any("Colors are the palette" in t for t in inline),
        False,
    )
    check(
        "a doc comment above a struct field is not an inline target",
        any("Name is what the thing" in t for t in inline),
        False,
    )
    check_true(
        "a comment inside a function body is an inline target",
        any("zero size is deliberate" in t for t in inline),
    )
    check(
        "inline target IDs remain unique when opening words collide",
        len({t["id"] for t in types_file["targets"] if t["kind"] == "inline"}),
        len([t for t in types_file["targets"] if t["kind"] == "inline"]),
    )
    check_true(
        "a comment above a function-local group is an inline target",
        any("grouped declaration inside a function" in t for t in inline),
    )

    # ------------------------------------------------------------ machine-read text is filtered

    reasons = " ".join(
        s["reason"] for f in path_payload["files"] for s in f.get("skippedComments", [])
    )
    check("a TODO marker is not a target", "TODO" in joined, False)
    check("a nolint directive is not a target", "nolint" in joined, False)
    check("a kubebuilder marker is not a target", "+kubebuilder" in joined, False)
    check_true("the skipped comments are reported with a reason", reasons.strip())

    # ------------------------------------------------------------ a documented struct field

    name_field = [
        t for t in types_file["targets"] if t["kind"] == "doc" and t["qualifiedName"].endswith("Name")
    ]
    check("the struct field is a target", len(name_field), 1)
    check(
        "a commented struct field is not reported as undocumented",
        name_field[0]["class"] if name_field else None,
        "unchanged",
    )

    # ------------------------------------------------------------ marker blocks

    check(
        "a comment group of markers only is not a doc comment",
        [t["class"] for t in types_file["targets"] if t["kind"] == "doc" and t["qualifiedName"].endswith("Note")],
        ["undocumented"],
    )
    weight = [
        t for t in types_file["targets"] if t["kind"] == "doc" and t["qualifiedName"].endswith("Weight")
    ]
    check("a documented field whose group ends in markers is documented", len(weight), 1)
    check(
        "…and is not reported as undocumented",
        weight[0]["class"] if weight else None,
        "unchanged",
    )
    check(
        "a standalone marker block is not an inline target",
        any("+kubebuilder:object:root" in t or "+optional" in t for t in inline),
        False,
    )

    # ------------------------------------------------------------ pairs

    pairs_out = run(
        root, "pairs", "--targets", out, "--file", "go/api/untouched.go", "--pre-sweep-ref", "HEAD"
    ).stdout
    pair = json.loads(pairs_out)
    entries = pair["targets"] if isinstance(pair, dict) else pair
    check_true("pairs returns the untouched file's targets", entries)
    if entries:
        first = entries[0]
        check(
            "in path scope an untouched comment is identical in all three versions",
            first.get("before") == first.get("preSweep") == first.get("after"),
            True,
        )

    pair = json.loads(
        run(root, "pairs", "--targets", out, "--file", "go/api/types.go", "--pre-sweep-ref", "HEAD").stdout
    )
    entries = pair["targets"] if isinstance(pair, dict) else pair
    w = [e for e in entries if e.get("qualifiedName", "").endswith("Weight")]
    check("pairs finds the marker-terminated field", len(w), 1)
    if w:
        check_true(
            "pairs carries the prose of a group that ends in markers, not an empty string",
            "Weight is documented" in (w[0].get("before") or ""),
        )
        check_true(
            "…on the after side too",
            "Weight is documented" in (w[0].get("after") or ""),
        )

    survey(root, out)  # back to diff scope, so pairs sees the edited comment
    pair = json.loads(
        run(root, "pairs", "--targets", out, "--file", "go/api/types.go", "--pre-sweep-ref", "HEAD").stdout
    )
    entries = pair["targets"] if isinstance(pair, dict) else pair
    build = [e for e in entries if e.get("qualifiedName", "").endswith("Build")]
    check("pairs finds the edited declaration", len(build), 1)
    if build:
        check(
            "pairs shows the branch's own edit as before/after",
            build[0]["before"] != build[0]["after"],
            True,
        )

    # ------------------------------------------------------------ Java identity and inline reconstruction

    java_payload = survey(root, out, "--paths", "java")
    jf = targets_of(java_payload, "java/A.java")
    check_true("the Java file is surveyed", jf["targets"])
    check("the Java file reports its language", jf.get("language"), "java")
    j_inline = [t["text"] for t in jf["targets"] if t["kind"] == "inline"]
    check(
        "a Javadoc block is not an inline target",
        any("Returns the answer" in t for t in j_inline),
        False,
    )
    check_true(
        "a Java // comment inside a method is an inline target",
        any("why forty-two" in t for t in j_inline),
    )
    inline_ids = [t["id"] for t in jf["targets"] if t["kind"] == "inline"]
    check("Java inline target IDs are unique", len(set(inline_ids)), len(inline_ids))

    package_file = targets_of(java_payload, "java/package-info.java")
    check_true("package-info Javadoc is a doc target", package_file["targets"])
    licensed_java = targets_of(java_payload, "java/Licensed.java")
    check(
        "a regular Java file never treats its license as package documentation",
        any(t.get("declKind") == "package" for t in licensed_java["targets"]),
        False,
    )
    overloads = [
        t for t in jf["targets"] if t["kind"] == "doc" and t["qualifiedName"].endswith("answer")
    ]
    check("both Java overloads are targets", len(overloads), 2)
    check("Java overload target IDs are unique", len({t["id"] for t in overloads}), 2)
    overload_pairs = json.loads(
        run(root, "pairs", "--targets", out, "--file", "java/A.java", "--pre-sweep-ref", "HEAD").stdout
    )["targets"]
    overload_docs = {
        p.get("signature"): p.get("after")
        for p in overload_pairs
        if p["kind"] == "doc" and p["qualifiedName"].endswith("answer")
    }
    check_true(
        "pairs keeps the no-argument overload's comment",
        "Returns the answer" in (overload_docs.get("public int answer()") or ""),
    )
    check_true(
        "pairs keeps the renamed-parameter overload's comment",
        "Returns the supplied answer" in (overload_docs.get("public int answer(int input)") or ""),
    )
    renamed_pair = [
        p
        for p in overload_pairs
        if p.get("signature") == "public int answer(int input)"
    ]
    check_true(
        "pairs matches the renamed-parameter overload to its before-version",
        renamed_pair and "Returns the supplied answer" in (renamed_pair[0].get("before") or ""),
    )

    write("java/A.java", JAVA_EDITED.replace("// why forty-two", "// The fixed answer is intentional."))
    inline_pairs = json.loads(
        run(root, "pairs", "--targets", out, "--file", "java/A.java", "--pre-sweep-ref", "HEAD").stdout
    )["targets"]
    rewritten_inline = [
        p for p in inline_pairs
        if p["kind"] == "inline" and "fixed answer is intentional" in (p.get("after") or "")
    ]
    check("pairs keeps one rewritten inline target", len(rewritten_inline), 1)
    if rewritten_inline:
        check_true(
            "pairs reads inline preSweep text from the rollback ref",
            "why forty-two" in (rewritten_inline[0].get("preSweep") or ""),
        )
        check_true(
            "pairs reads rewritten inline text from disk",
            "fixed answer is intentional" in (rewritten_inline[0].get("after") or ""),
        )
        check_true("pairs marks an inline rewrite as touched", rewritten_inline[0].get("touchedBySweep"))
    write("java/A.java", JAVA_EDITED)

    deletion_payload = survey(root, out)
    deletion_file = targets_of(deletion_payload, "java/DeleteMe.java")
    deleted_doc = [t for t in deletion_file["targets"] if t["kind"] == "doc"]
    deleted_inline = [t for t in deletion_file["targets"] if t["kind"] == "inline"]
    check_true("a pure doc-comment deletion creates a declaration target", deleted_doc)
    check_true("a pure inline-comment deletion creates an inline target", deleted_inline)
    if deleted_inline:
        check_true("a deleted inline target is marked deleted", deleted_inline[0].get("deleted"))
    deletion_pairs = json.loads(
        run(root, "pairs", "--targets", out, "--file", "java/DeleteMe.java", "--pre-sweep-ref", "HEAD").stdout
    )["targets"]
    deleted_doc_pair = [p for p in deletion_pairs if p["kind"] == "doc" and p.get("declKind") == "method"]
    deleted_inline_pair = [p for p in deletion_pairs if p["kind"] == "inline"]
    if deleted_doc_pair:
        check_true("pairs retains a deleted doc comment as before", deleted_doc_pair[0].get("before"))
        check("pairs reports a deleted doc comment as absent after", bool(deleted_doc_pair[0].get("after")), False)
    if deleted_inline_pair:
        check_true("pairs retains a deleted inline comment as before", deleted_inline_pair[0].get("before"))
        check("pairs reports a deleted inline comment as absent after", deleted_inline_pair[0].get("after"), None)

    # ------------------------------------------------------------ ledger scope

    ledger = str(Path(root) / "ledger.json")
    run(
        root,
        "ledger",
        "--root", root,
        "--ledger", ledger,
        "--mode", "diff",
        "--base", git(root, "merge-base", "HEAD", "HEAD").strip(),
        "--files", "java/A.java",
    )
    resumed_diff = survey(root, out, "--ledger", ledger)
    check(
        "a matching diff ledger resumes the file",
        any(item["path"] == "java/A.java" for item in resumed_diff["files"]),
        False,
    )
    path_after_diff = survey(root, out, "--paths", "java", "--ledger", ledger)
    check_true(
        "a diff ledger does not suppress a path audit",
        targets_of(path_after_diff, "java/A.java")["targets"],
    )

    latin = Path(root) / "java/Latin.java"
    latin.write_bytes(b"package p; // caf\xe9\nclass Latin {}\n")
    subprocess.run(["git", "-C", root, "add", "java/Latin.java"], check=True, capture_output=True)
    subprocess.run(["git", "-C", root, "commit", "-qm", "latin-1"], check=True, capture_output=True)
    try:
        shown = git(root, "show", "HEAD:java/Latin.java")
        check_true("Git text preserves non-UTF-8 bytes with surrogateescape", shown)
    except UnicodeDecodeError:
        check("Git text preserves non-UTF-8 bytes with surrogateescape", "UnicodeDecodeError", "text")

    # ------------------------------------------------------------ a file the scanner cannot read

    write("go/api/broken.go", 'package api\n\nvar s = "unterminated\n')
    subprocess.run(["git", "-C", root, "add", "-A"], check=True, capture_output=True)
    broken_payload = survey(root, out, "--paths", "go/api")
    bf = targets_of(broken_payload, "go/api/broken.go")
    check_true("an unlexable file is reported", bf)
    check_true("an unlexable file degrades instead of failing the run", bf and bf["degraded"])
    check_true(
        "the other files still survey normally",
        targets_of(broken_payload, "go/api/untouched.go")["targets"],
    )

# ---------------------------------------------------------------- report

if FAILURES:
    print(f"{len(FAILURES)} failed:\n")
    for f in FAILURES:
        print(f"  - {f}\n")
    sys.exit(1)
print("all cases pass")
