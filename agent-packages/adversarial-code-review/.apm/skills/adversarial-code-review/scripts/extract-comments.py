#!/usr/bin/env python3
"""Print every comment block a change adds or edits, each with the first code line after it.

Usage: extract-comments.py <repo> <base> [<file>...]

<repo> is a checkout at the reviewed head. Without files, every file the change touches is read. Line numbers are at
HEAD. Recognizes `//` and `/* ... */` comments, and `#` comments and docstrings in Python, shell, Ruby, YAML, and
TOML files; other syntaxes, such as `--` comments, are not extracted.
"""
import os
import re
import subprocess
import sys

HASH_COMMENT = {".py", ".sh", ".bash", ".rb", ".yml", ".yaml", ".toml", ".properties"}
FENCE = {".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust", ".ts": "ts", ".js": "js", ".py": "python",
         ".scala": "scala", ".groovy": "groovy", ".c": "c", ".h": "c", ".cpp": "cpp", ".cs": "csharp"}


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=True).stdout


def added_lines(repo, base, path):
    diff = git(repo, "diff", "-U0", f"{base}...HEAD", "--", path)
    added = set()
    for m in re.finditer(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", diff, re.M):
        start, n = int(m.group(1)), int(m.group(2) or 1)
        added.update(range(start, start + n))
    return added


def blocks(lines, hash_comments):
    """Yield (first, last, code) line indexes of each comment block.

    `code` is the declaration the block documents: the line after a comment, or the line before a Python docstring.
    """
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        quote = next((q for q in ('"""', "'''") if s.startswith(q)), None) if hash_comments else None
        if quote:
            j = i
            if s.count(quote) < 2:
                j += 1
                while j < len(lines) - 1 and quote not in lines[j]:
                    j += 1
            k = i - 1
            while k > 0 and not lines[k].strip():
                k -= 1
            yield i, j, k
            i = j + 1
            continue
        if s.startswith("/*"):
            j = i
            while j < len(lines) - 1 and "*/" not in lines[j]:
                j += 1
        elif s.startswith("//") or (hash_comments and s.startswith("#") and not s.startswith("#!")):
            prefix = "//" if s.startswith("//") else "#"
            j = i
            while j + 1 < len(lines) and lines[j + 1].strip().startswith(prefix):
                j += 1
        else:
            i += 1
            continue
        k = j + 1
        while k < len(lines) and (not lines[k].strip() or lines[k].strip().startswith("@")):
            k += 1
        yield i, j, k
        i = j + 1


def is_license(lines, block):
    """A file's opening comment that carries a copyright or license notice."""
    first, last, _ = block
    body = "\n".join(lines[first:last + 1]).lower()
    return all(not lines[n].strip() for n in range(first)) and ("copyright" in body or "license" in body)


def main():
    repo, base, files = sys.argv[1], sys.argv[2], sys.argv[3:]
    if not files:
        files = git(repo, "diff", "--name-only", "--diff-filter=AMR", f"{base}...HEAD").split()
    for path in files:
        try:
            text = git(repo, "show", f"HEAD:{path}")
        except subprocess.CalledProcessError:
            continue
        ext = os.path.splitext(path)[1]
        added = added_lines(repo, base, path)
        lines = text.split("\n")
        found = [b for b in blocks(lines, ext in HASH_COMMENT)
                 if any(n + 1 in added for n in range(b[0], b[1] + 1)) and not is_license(lines, b)]
        if not found:
            continue
        print(f"## {path}\n")
        for i, j, k in found:
            print(f"### lines {i + 1}-{j + 1}")
            print(f"```{FENCE.get(ext, '')}")
            if 0 <= k < i:
                print(f"{k + 1:5d}  {lines[k]}")
            for n in range(i, j + 1):
                print(f"{n + 1:5d}  {lines[n]}")
            if j < k < len(lines):
                print(f"{k + 1:5d}  {lines[k]}")
            print("```\n")


if __name__ == "__main__":
    main()
