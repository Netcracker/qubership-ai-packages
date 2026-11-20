#!/usr/bin/env python3
"""List the members a change touched and whether their doc comment moved with the code.

Usage: comment-drift.py <base-ref> [<head-ref>]   (head defaults to the working tree, untracked files included)
       comment-drift.py --history <base-ref> [<head-ref>]

For every changed Java, Kotlin, Groovy, or Scala file, prints one line per member whose code or doc
comment changed, as "<member> @<line>: <tag>", where the line is the declaration's line in the head
version (in the base version, prefixed "base ", for a member the change removed) and the tag is one of:

  code-changed, comment-unchanged   the body moved and the doc comment above it did not: re-read it
  comment-added                     a doc comment that did not exist before
  comment-changed                   both, or the comment alone
  code-changed, no-comment          the body moved and the member has no doc comment

A member is named with its enclosing type and its parameter types, so overloads and same-named
members of two types are reported apart: Reader.read(int) and Reader.read(String) are two lines,
and Writer.read(int) a third. The member is the nearest declaration above the changed line; the
enclosing type is the nearest type declaration above it with a smaller indentation. The parse is
line-based and approximate: a val or var indented deeper than the last open function is a local and
belongs to that function; a line the parse cannot place is reported under the file with tag "unplaced".
Paths are printed relative to the repository root, whichever directory the script runs from.

With --history, prints instead every member whose code HISTORY_MIN or more commits of <base>..<head>
changed, with the subject of each commit; without <head>, the uncommitted change counts as one more.
Files of a test source set are left out: a test class gains one method per case by design. A member
is keyed on its bare name: two overloads, or one member the parse placed under two enclosing types,
count as one member.
A member that commit after commit edits is where a branch may be adding one case per fix.
"""
import difflib
import os
import re
import shutil
import subprocess
import sys
import tempfile

EXT = (".java", ".kt", ".kts", ".groovy", ".scala")
DECL = re.compile(
    r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*"
    r"(?:(?:public|private|protected|static|final|abstract|synchronized|native|default|override|open|inline|"
    r"suspend|internal|sealed|data|const|lateinit)\s+)*"
    r"(?:(?:class|interface|enum|record|object)\s+(\w+)"
    r"|(?:fun|def)\s+(?:<[^>]*>\s*)?(?:[\w.]+\.)?(\w+)\s*(?:\((.*)$|(?=[:=\s]|$))"
    r"|(?:val|var)\s+(\w+)"
    r"|(?!(?:return|new|throw|else|case)\b)[\w<>\[\]?][\w<>\[\],.? ]*?\s+"
    r"(?!(?:if|for|while|switch|catch|try|synchronized|return|new|else|throws)\b)(\w+)\s*\((.*)$)")
TYPE_DECL = re.compile(r"^(\s*)(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|private|protected|static|final|abstract|sealed|data|open|internal|inner|enum|annotation)\s+)*"
                       r"(?:class|interface|enum|record|object|trait)\s+(\w+)")
ANNOTATION = re.compile(r"@\w+(?:\([^)]*\))?")
HISTORY_MIN = 3
# Characters of deleted-path arguments one `git diff` may carry: Windows caps a whole command line at 32767.
RENAME_SOURCES_BUDGET = 24000


def run(*args, env=None, stdin=None):
    """The stdout of a git command, decoded as UTF-8 whatever the locale says.

    Paths on disk are bytes, and a path the locale cannot decode keeps its bytes through
    errors="surrogateescape", so open() and `git show` find the file the diff named. ``env`` adds
    variables to the inherited environment, and ``stdin`` is written to the command's input."""
    return subprocess.run(["git", *args], capture_output=True, check=True, input=stdin,
                          encoding="utf-8", errors="surrogateescape",
                          env={**os.environ, **env} if env else None).stdout


def uncommitted_listing():
    """The --name-status listing of the JVM sources in the working tree against HEAD, renames followed.

    `git diff HEAD` sees only the deleted side of a rename whose new path is untracked, so the
    untracked sources are marked intent-to-add in a copy of the index; the real index is not
    touched. Intent-to-add writes no blob, and the pathspec keeps git from reading, or running the
    clean filter of, any file that is not a JVM source. The pathspec also names every deleted path,
    so that a source renamed back from another extension stays one file; git reads a deleted path
    from HEAD, not from the disk. Where those paths would take more than RENAME_SOURCES_BUDGET
    characters of the command line, it names none, and such a rename starts a new history. Every
    path from a git listing passes as a literal pathspec, so a file named ":(exclude)Reader.java" is that file."""
    tmp = tempfile.mkdtemp(prefix="comment-drift-")
    try:
        env = {"GIT_INDEX_FILE": os.path.join(tmp, "index")}
        real = run("rev-parse", "--git-path", "index").strip()
        if os.path.exists(real):
            shutil.copyfile(real, env["GIT_INDEX_FILE"])
        else:
            run("read-tree", "HEAD", env=env)
        sources = [f"*{ext}" for ext in EXT]
        deleted = set(nul_split(run("ls-files", "--deleted", "-z", env=env)))
        deleted |= set(nul_split(run("diff", "--cached", "--no-renames", "--name-only", "-z", "--diff-filter=D",
                                     "HEAD", env=env)))
        renamed_from = [f":(literal){p}" for p in sorted(deleted)]
        if sum(len(a) + 1 for a in renamed_from) > RENAME_SOURCES_BUDGET:
            renamed_from = []
        untracked = nul_split(run("ls-files", "--others", "--exclude-standard", "-z", "--", *sources))
        if untracked:
            run("add", "--intent-to-add", "--pathspec-from-file=-", "--pathspec-file-nul", env=env,
                stdin="".join(f":(literal){p}\0" for p in untracked))
        return run("diff", "-M", "--name-status", "-z", "HEAD", "--", *sources, *renamed_from, env=env)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def nul_split(out):
    r"""The paths of a NUL-delimited git listing.

    Git quotes a path outside ASCII in its default output, so a file named "Пример.java" comes back
    as "\320\237...\321\200.java" — trailing quote and all — and drops out of the extension filter.
    A -z listing is unquoted, so the path arrives verbatim."""
    return [p for p in out.split("\0") if p]


def lines_of(ref, path):
    if ref is None:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read().splitlines()
        except FileNotFoundError:
            return []
    try:
        return run("show", f"{ref}:{path}").splitlines()
    except subprocess.CalledProcessError:
        return []


def split_params(text):
    """Split a parameter list on the commas outside angle brackets and parentheses."""
    parts, depth, cur = [], 0, []
    for ch in text:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def param_types(rest):
    """The parameter types of a declaration, from the text after its opening parenthesis.

    Names are dropped, so a renamed parameter keeps the member's identity; a list that continues on
    the next line is cut where the line ends and marked with an ellipsis."""
    depth, end = 1, None
    for i, ch in enumerate(rest):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                end = i
                break
    inner = rest if end is None else rest[:end]
    types = []
    for p in split_params(inner):
        p = ANNOTATION.sub("", p).replace("final ", "").strip()
        if ":" in p:  # Kotlin and Scala: name: Type
            p = p.split(":", 1)[1].strip()
        else:
            tokens = p.split()
            if len(tokens) > 1:
                p = " ".join(tokens[:-1])
        types.append(re.sub(r"\s+", " ", p))
    joined = ", ".join(types)
    return joined + ("…" if end is None else "")


def member_of(match):
    """The member's own name: a type name, a val/var name, or name(parameter types) for a function."""
    if match.group(1):
        return match.group(1)
    if match.group(2):
        if match.group(3) is None:  # Scala `def size = 0`, a parameterless member
            return match.group(2)
        return f"{match.group(2)}({param_types(match.group(3))})"
    if match.group(4):
        return match.group(4)
    return f"{match.group(5)}({param_types(match.group(6))})"


def enclosing_types(lines, in_doc):
    """For each line, the dotted path of the type declarations above it with a smaller indentation."""
    out = []
    stack = []  # (indent, name)
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("}") and stack:
            indent = len(line[: len(line) - len(stripped)].expandtabs(4))
            while stack and stack[-1][0] >= indent:
                stack.pop()
        m = TYPE_DECL.match(line) if not in_doc[i] else None
        if m:
            indent = len(m.group(1).expandtabs(4))
            while stack and stack[-1][0] >= indent:
                stack.pop()
            out.append(".".join(n for _, n in stack))
            stack.append((indent, m.group(2)))
        else:
            out.append(".".join(n for _, n in stack))
    return out


def annotate(lines):
    """For each line: (in_doc_comment, member, decl_line) where member is the nearest declaration.

    A doc comment belongs to the declaration that follows it, so its lines are attributed forward;
    every other line belongs to the declaration above it. decl_line is 1-based."""
    in_doc = []
    state = False
    for line in lines:
        s = line.strip()
        if s.startswith("/**"):
            state = True
        in_doc.append(state)
        if "*/" in s:
            state = False
    scopes = enclosing_types(lines, in_doc)
    decls = [None] * len(lines)
    funcs = []  # indentation of each function body still open, innermost last
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = len(line[: len(line) - len(stripped)].expandtabs(4))
        if stripped.startswith("}"):
            while funcs and funcs[-1] >= indent:
                funcs.pop()
        m = DECL.match(line)
        if not m or in_doc[i]:
            continue
        while funcs and funcs[-1] >= indent:
            funcs.pop()
        if m.group(4) and funcs and indent > funcs[-1]:
            continue  # a val or var inside a function body is a local, and belongs to that function
        name = member_of(m)
        decls[i] = (f"{scopes[i]}.{name}" if scopes[i] else name, i + 1)
        if m.group(2) or m.group(5):
            funcs.append(indent)
    above = [None] * len(lines)
    current = None
    for i in range(len(lines)):
        current = decls[i] or current
        above[i] = current
    below = [None] * len(lines)
    nxt = None
    for i in range(len(lines) - 1, -1, -1):
        nxt = decls[i] or nxt
        below[i] = nxt
    out = []
    for i in range(len(lines)):
        d = below[i] if in_doc[i] else above[i]
        out.append((in_doc[i], d[0] if d else None, d[1] if d else None))
    return out


def main():
    args = sys.argv[1:]
    history = args[:1] == ["--history"]
    if history:
        args = args[1:]
    if not args:
        sys.exit(__doc__)
    base = args[0]
    head = args[1] if len(args) > 1 else None
    sys.stdout.reconfigure(encoding="utf-8", errors="surrogateescape")
    os.chdir(run("rev-parse", "--show-toplevel").strip())
    if history:
        print_history(base, head)
        return
    diff_args = ["diff", "--name-only", "-z", base] + ([head] if head else [])
    files = nul_split(run(*diff_args))
    if head is None:
        files += nul_split(run("ls-files", "--others", "--exclude-standard", "-z"))
    files = [f for f in files if f.endswith(EXT)]
    for path in files:
        old, new = lines_of(base, path), lines_of(head, path)
        old_ann, new_ann = annotate(old), annotate(new)
        touched = {}  # member -> {"code": bool, "comment": bool}
        where = {}  # member -> location string
        unplaced = 0
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
            if tag == "equal":
                continue
            for k in range(i1, i2):
                doc, member, line = old_ann[k]
                _mark(touched, member, doc)
                where.setdefault(member, f"base {line}")
                unplaced += member is None
            for k in range(j1, j2):
                doc, member, line = new_ann[k]
                _mark(touched, member, doc)
                where[member] = str(line)
                unplaced += member is None
        old_members_with_doc = {m for (doc, m, _) in old_ann if doc}
        new_members_with_doc = {m for (doc, m, _) in new_ann if doc}
        print(f"== {path}")
        for member, t in sorted(touched.items(), key=lambda kv: str(kv[0])):
            if member is None:
                continue
            if t["comment"] and member not in old_members_with_doc and member in new_members_with_doc:
                tag = "comment-added"
            elif t["comment"]:
                tag = "comment-changed"
            elif member in new_members_with_doc:
                tag = "code-changed, comment-unchanged"
            else:
                tag = "code-changed, no-comment"
            print(f"  {member} @{where[member]}: {tag}")
        if unplaced:
            print(f"  (file level): {unplaced} changed line(s) unplaced")


def code_members(old, new):
    """The members whose code, not only their doc comment, differs between two versions of a file."""
    old_ann, new_ann = annotate(old), annotate(new)
    out = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        out.update(m for doc, m, _ in old_ann[i1:i2] if m and not doc)
        out.update(m for doc, m, _ in new_ann[j1:j2] if m and not doc)
    return out


def bare_name(member):
    """The member's name without its enclosing types and its parameter list: Outer.Inner.f(int) is f.

    The enclosing-type path the line parse gives a member can change from one commit to the next (a
    nested type declared on one line shifts it), and so can the parameter list, so the history keys a
    member on this name; overloads in one file then count together."""
    return member.split("(", 1)[0].rsplit(".", 1)[-1]


def is_test_path(path):
    """Whether a directory of ``path`` names a test source set: test or tests in any case, or a
    camel-case name that starts with test or ends with Test or Tests (testFixtures, integrationTest,
    unitTests). latest and contest are not test directories."""
    return any(seg.lower() in ("test", "tests") or re.fullmatch(r"[Tt]est[A-Z]\w*|[a-z]\w*Tests?", seg)
               for seg in path.split("/")[:-1])


def changed_paths(listing):
    """(status letter, path before, path after) triples of a NUL-delimited --name-status listing, renames followed."""
    fields = nul_split(listing)
    out, i = [], 0
    while i < len(fields):
        status = fields[i]
        if status[0] in "RC":
            out.append((status[0], fields[i + 1], fields[i + 2]))
            i += 3
        else:
            out.append((status[0], fields[i + 1], fields[i + 1]))
            i += 2
    return out


def head_has(head):
    """A predicate that tells whether a path exists in <head>, or in the working tree where head is None."""
    if head is None:
        return os.path.isfile
    present = set(nul_split(run("ls-tree", "-r", "--name-only", "-z", head)))
    return present.__contains__


def print_history(base, head):
    """Print, per file, the members whose code HISTORY_MIN or more steps of the branch changed.

    A step is a non-merge commit of <base>..<head>, oldest first, and, where <head> is the working
    tree, the uncommitted change as a last step. A step counts once per member however many of its
    hunks touch it. A renamed file keeps its members' counts. A file added at a path starts a
    history of its own, including at a path that a rename or a deletion freed and at a path that a
    revert restores. Each file is reported under the last of its paths that exists in <head> and
    that no later step gave to another file, and a file with none is left out. With merges in the
    range, "later" is the order of the walk, not the order in which the paths replaced one another."""
    shas = run("rev-list", "--reverse", "--no-merges", f"{base}..{head or 'HEAD'}").split()
    steps = [(sha, f"{sha}^", sha, run("log", "-1", "--format=%h %s", sha).strip()) for sha in shas]
    if head is None:
        steps.append((None, "HEAD", None, "(uncommitted)"))
    file_of = {}  # path -> the index in paths of the file that holds it
    paths = []  # for each file, every path it had, in walk order
    edits = {}  # (file, bare name) -> [step label]
    names = {}  # (file, bare name) -> {full member names seen}
    for sha, before, after, label in steps:
        listing = run("diff-tree", "--no-commit-id", "-r", "-M", "--name-status", "-z", sha) if sha \
            else uncommitted_listing()
        for status, old, new in changed_paths(listing):
            if status == "A" or old not in file_of:
                file_of[old] = len(paths)
                paths.append([old])
            file = file_of[new] = file_of[old]
            if new not in paths[file]:
                paths[file].append(new)
            if not new.endswith(EXT):
                continue
            members = code_members([] if status == "A" else lines_of(before, old), lines_of(after, new))
            for bare in {bare_name(m) for m in members}:
                edits.setdefault((file, bare), []).append(label)
                names.setdefault((file, bare), set()).update(m for m in members if bare_name(m) == bare)
    exists = head_has(head)
    surviving = [next((p for p in reversed(ps) if exists(p) and file_of[p] == file), None)
                 for file, ps in enumerate(paths)]
    current = None
    for (file, bare), labels in sorted(edits.items(), key=lambda kv: (surviving[kv[0][0]] or "", kv[0])):
        path = surviving[file]
        if len(labels) < HISTORY_MIN or path is None or not path.endswith(EXT) or is_test_path(path):
            continue
        if file != current:
            print(f"== {path}")
            current = file
        print(f"  {bare}: {len(labels)} commits ({'; '.join(sorted(names[(file, bare)]))})")
        for label in labels:
            print(f"    {label}")


def _mark(touched, member, doc):
    t = touched.setdefault(member, {"code": False, "comment": False})
    t["comment" if doc else "code"] = True


if __name__ == "__main__":
    main()
