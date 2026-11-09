#!/usr/bin/env python3
"""Print every comment block a change adds or edits, each with the first code line after it.

Usage: extract-comments.py <repo> <base> [<file>...]

<repo> is a checkout at the reviewed head. Without files, every file the change touches is read. Line numbers are at
HEAD. Recognizes `//` and `/* ... */` comments, and `#` comments and docstrings in Python, shell, Ruby, YAML, and
TOML files; other syntaxes, such as `--` comments, are not extracted. A file that is not UTF-8 text, or that HEAD
does not have, is skipped with a note on stderr.
"""
import os
import re
import subprocess
import sys

HASH_COMMENT = {".py", ".sh", ".bash", ".rb", ".yml", ".yaml", ".toml", ".properties"}
FENCE = {".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust", ".ts": "ts", ".js": "js", ".py": "python",
         ".scala": "scala", ".groovy": "groovy", ".c": "c", ".h": "c", ".cpp": "cpp", ".cs": "csharp"}


def git(repo, *args, text=True):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=text, check=True).stdout


def read_text(repo, path):
    """Return the file at HEAD as text, or None, with a note on stderr, where it is missing or not UTF-8 text."""
    try:
        data = git(repo, "show", f"HEAD:{path}", text=False)
    except subprocess.CalledProcessError:
        print(f"extract-comments: skipped {path}: not in HEAD", file=sys.stderr)
        return None
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = None
    if text is None or "\0" in text:
        print(f"extract-comments: skipped {path}: not UTF-8 text", file=sys.stderr)
        return None
    return text


def added_lines(repo, base, path):
    # Only the hunk headers are read, and a removed line may be in another encoding than the file at HEAD.
    diff = git(repo, "diff", "-U0", f"{base}...HEAD", "--", path, text=False).decode("utf-8", "replace")
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
        names = git(repo, "diff", "--name-only", "-z", "--diff-filter=AMR", f"{base}...HEAD", text=False)
        files = [os.fsdecode(p) for p in names.split(b"\0") if p]
    for path in files:
        text = read_text(repo, path)
        if text is None:
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
