#!/usr/bin/env python3
"""Print every doc comment a change adds or edits, a deletion inside it included, with the declaration it documents.

Usage: extract-comments.py --diff-base <base> [--repo <repo>]

<repo> is a checkout at the reviewed head, the current directory by default. Line numbers are at HEAD. Declarations and
their doc comments come from `sb map` (ast-bro), so only a comment sb attaches to a declaration is printed: a module
docstring, a Go package comment, a `//` comment above a Java member, and a comment inside a body are not. A changed
file in which sb finds no declaration, or that HEAD holds as something other than a file, such as a submodule, is
printed as its diff. Where `sb` is not on PATH, or fails, the whole diff is printed instead, with a note on stderr.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, check=True).stdout


def touched_lines(repo, base, path):
    """Return the HEAD line numbers the change added, and for each deletion-only hunk the two lines around the gap."""
    # Only the hunk headers are read, and a removed line may be in another encoding than the file at HEAD.
    diff = git(repo, "diff", "-U0", f"{base}...HEAD", "--", path).decode("utf-8", "replace")
    touched = set()
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", diff, re.M):
        start, n = int(m.group(1)), int(m.group(2) or 1)
        touched.update(range(start, start + n) if n else (start, start + 1))
    return touched


def outline(paths):
    """Return (language, declarations) for each of paths sb outlines, keyed by path, or None, with a note on stderr,
    where sb is missing or fails.

    A path sb skips, or whose outline holds no declaration, is not a key.
    """
    if not shutil.which("sb"):
        print("extract-comments: sb is not on PATH; printing the diff instead."
              " sb is the CLI of ast-bro: https://github.com/aeroxy/ast-bro", file=sys.stderr)
        return None
    result = subprocess.run(["sb", "map", "--json", "--compact", *paths], capture_output=True)
    try:
        files = json.loads(result.stdout)["files"]
    except (ValueError, KeyError):
        reason = result.stderr.decode("utf-8", "replace").strip().splitlines()
        print(f"extract-comments: sb map exited with {result.returncode}"
              f"{': ' + reason[0] if reason else ''}; printing the diff instead", file=sys.stderr)
        return None
    return {f["path"]: (f["language"], f["declarations"]) for f in files if f["declarations"]}


def documented(declarations, data, scope=()):
    """Yield (qualified name, first doc line, last doc line, declaration) for each declaration that has a doc comment.

    Lines are 1-based. A doc comment inside the body, such as a Python docstring, is found by its first line.
    """
    for d in declarations:
        name = scope + (d["name"],)
        if d.get("docs"):
            if d["docs_inside"]:
                text = "\n".join(d["docs"])
                at = data.find(text.split("\n")[0].strip().encode("utf-8"), d["start_byte"])
                if at >= 0:
                    first = data.count(b"\n", 0, at) + 1
                    yield name, first, first + text.count("\n"), d
            elif d["doc_start_byte"] < d["start_byte"]:
                yield name, data.count(b"\n", 0, d["doc_start_byte"]) + 1, d["start_line"] - 1, d
        yield from documented(d.get("children", ()), data, name)


def report(path, data, declarations, touched, language):
    lines = data.decode("utf-8-sig", "replace").split("\n")
    found = [b for b in documented(declarations, data) if any(n in touched for n in range(b[1], b[2] + 1))]
    if not found:
        return
    print(f"## {path}\n")
    for name, first, last, d in sorted(found, key=lambda b: b[1]):
        # The declaration's own line: the first line that names it and is not an annotation or a decorator.
        own = next((n for n in range(d["start_line"], d["end_line"] + 1)
                    if not lines[n - 1].lstrip().startswith("@")
                    and re.search(rf"\b{re.escape(d['name'])}\b", lines[n - 1])), d["start_line"])
        shown = sorted(set(range(first, last + 1)) | set(range(d["start_line"], own + 1)))
        print(f"### lines {first}-{last}: {'.'.join(name)}")
        print(f"```{language}")
        for n in shown:
            print(f"{n:5d}  {lines[n - 1]}")
        print("```\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--diff-base", required=True, help="the commit the change is compared with, as in base...HEAD")
    parser.add_argument("--repo", default=".", help="a checkout at the reviewed head (default: the current directory)")
    args = parser.parse_args()
    repo, base = args.repo, args.diff_base
    names = git(repo, "diff", "--name-only", "-z", "--diff-filter=AMR", f"{base}...HEAD")
    paths = [os.fsdecode(p) for p in names.split(b"\0") if p]
    with tempfile.TemporaryDirectory() as tmp:
        # sb reads the file at HEAD, not the working tree, so its line numbers match the diff.
        copies = {}
        for path in paths:
            # A regular file has mode 100644 or 100755; a submodule's commit is not in this repository to show.
            if not git(repo, "--literal-pathspecs", "ls-tree", "-z", "HEAD", "--", path).startswith(b"100"):
                copies[path] = None
                continue
            copy = os.path.join(tmp, path)
            os.makedirs(os.path.dirname(copy), exist_ok=True)
            with open(copy, "wb") as fh:
                fh.write(git(repo, "show", f"HEAD:{path}"))
            copies[path] = copy
        files = [copy for copy in copies.values() if copy]
        outlines = outline(files) if files else {}
        if outlines is None:
            sys.stdout.flush()
            sys.stdout.buffer.write(git(repo, "diff", f"{base}...HEAD"))
            return
        rest = []
        for path, copy in copies.items():
            if copy not in outlines:
                rest.append(path)
                continue
            with open(copy, "rb") as fh:
                data = fh.read()
            language, declarations = outlines[copy]
            report(path, data, declarations, touched_lines(repo, base, path), language)
        for path in rest:
            print(f"## {path}: sb found no declaration in it, so here is its diff\n")
            print("```diff")
            sys.stdout.flush()
            sys.stdout.buffer.write(git(repo, "diff", f"{base}...HEAD", "--", path))
            print("```\n")


if __name__ == "__main__":
    main()
