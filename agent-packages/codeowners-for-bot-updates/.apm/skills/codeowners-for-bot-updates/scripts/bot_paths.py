#!/usr/bin/env python3
"""List the files dependency bots change and propose ownerless CODEOWNERS lines.

Reads the bot pull requests of a GitHub repository (Renovate and Dependabot by
default) through `gh`, classifies each one as automerged or merged by hand, and
matches every changed path against CODEOWNERS with git's own wildmatch, one
pattern at a time, so the last matching line wins as it does on GitHub.

With --repo alone it reads the tree and CODEOWNERS of the default branch
through the GitHub API. With --repo-dir it reads them from origin/<base> of a
fetched clone, and also finds commits a bot pushed with no PR:

    python3 -I bot_paths.py --repo owner/name
    python3 -I bot_paths.py --repo owner/name --repo-dir <clone> --codeowners <edited file>

With --codeowners it checks an edited file instead and reports every path whose
last matching line disagrees with the verdict.
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict

# Patterns proposed whatever the history says: files bots update in almost
# every repository, so a file that appears later is already covered.
ALWAYS = ["/.github/workflows/", "*Dockerfile*", "docker-compose.yml", "docker-compose.yaml",
          "compose.yml", "compose.yaml", "*.gradle", "*.gradle.kts"]

# Ecosystem patterns, proposed when a detector file exists anywhere in the
# tree. "lfm" lists the lock files that Renovate lock file maintenance
# rewrites.
ECOSYSTEMS = [
    {"name": "go", "detect": ["go.mod"], "patterns": ["go.mod", "go.sum"]},
    {"name": "maven", "detect": ["pom.xml"],
     "patterns": ["pom.xml", "maven-wrapper.properties"]},
    {"name": "gradle", "detect": ["gradlew", "settings.gradle", "settings.gradle.kts"],
     "patterns": ["gradle-wrapper.properties", "gradle-wrapper.jar", "gradlew",
                  "gradlew.bat", "libs.versions.toml"]},
    {"name": "npm", "detect": ["package.json"], "patterns": ["package.json"],
     "lfm": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json"]},
    {"name": "python", "detect": ["pyproject.toml", "requirements.txt", "Pipfile"],
     "patterns": ["requirements*.txt", "pyproject.toml", "Pipfile"],
     "lfm": ["poetry.lock", "uv.lock", "Pipfile.lock"]},
    {"name": "cargo", "detect": ["Cargo.toml"], "patterns": ["Cargo.toml"],
     "lfm": ["Cargo.lock"]},
    # Chart.yaml lists the chart dependencies; values.yaml holds the chart
    # configuration as well as image tags, so it is no well-known name: it is
    # covered by path, or by name where bots update every copy in the tree.
    {"name": "helm", "detect": ["Chart.yaml"], "patterns": ["Chart.yaml"], "lfm": ["Chart.lock"]},
    # The files Renovate's helmfile manager reads by default.
    {"name": "helmfile",
     "detect": ["helmfile.yaml", "helmfile.yml", "helmfile.yaml.gotmpl", "helmfile.yml.gotmpl"],
     "patterns": ["helmfile.yaml", "helmfile.yml", "helmfile.yaml.gotmpl", "helmfile.yml.gotmpl",
                  "helmfile.d/"]},
    {"name": "mise", "detect": ["mise.toml", ".mise.toml", ".tool-versions"],
     "patterns": ["mise.toml", ".mise.toml", ".tool-versions"]},
    {"name": "pre-commit", "detect": [".pre-commit-config.yaml"],
     "patterns": [".pre-commit-config.yaml"]},
    # Files `apm install` deploys from apm.lock.yaml, so a lock file
    # maintenance PR rewrites them along with the lock file.
    {"name": "apm", "detect": ["apm.yml"],
     "patterns": ["/.agents/skills/", "/.claude/rules/", "/.claude/skills/", "/.cursor/rules/"],
     "lfm": ["apm.lock.yaml"]},
    {"name": "terraform", "detect": [".terraform.lock.hcl"], "patterns": [],
     "lfm": [".terraform.lock.hcl"]},
]

# Basenames generalised to an unanchored pattern when seen in bot history.
BASENAME_PATTERNS = {p for e in ECOSYSTEMS for p in e["patterns"] + e.get("lfm", [])
                     if "*" not in p and not p.startswith("/") and not p.endswith("/")} | {p for p in ALWAYS if not p.startswith("/")}

DIR_PATTERNS = ["/.github/workflows/", "/.github/actions/"] + \
    [p for e in ECOSYSTEMS for p in e["patterns"] if p.endswith("/")]

SOURCE_FILE = re.compile(r"\.(go|java|kt|scala|groovy|js|jsx|ts|tsx|py|rs|c|h|cpp|cs|rb|php|swift)$")

# The lines that delimit the generated block, so that a later run finds and
# replaces it.
BLOCK_BEGIN = "# BEGIN codeowners-for-bot-updates: files that bots update have no owner"
BLOCK_END = "# END codeowners-for-bot-updates"
BLOCK_COMMENT = """\
# A bot PR that changes only these files requests no review. The list holds
# the files that Renovate and Dependabot commits changed, plus file names
# that cover copies added later. Regenerate it with the
# codeowners-for-bot-updates skill instead of editing it:
# https://github.com/Netcracker/qubership-ai-packages/tree/main/agent-packages/codeowners-for-bot-updates
# The last matching line wins, so a line after the block gives the files it
# matches their owners back."""

RENOVATE_LOCATIONS = ["renovate.json", ".github/renovate.json", ".gitlab/renovate.json",
                      ".renovaterc", ".renovaterc.json"]

CODEOWNERS_LOCATIONS = [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"]

PR_QUERY = """
query($q: String!, $after: String) {
  search(query: $q, type: ISSUE, first: 50, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        number title body state createdAt mergedAt headRefName
        author { login }
        mergedBy { __typename login }
        autoMergeRequest { enabledAt }
        mergeCommit { oid }
        files(first: 100) { totalCount nodes { path } }
        commits(first: 100) {
          totalCount
          nodes { commit { oid parents { totalCount } author { name user { login } } } }
        }
      }
    }
  }
}
"""


def run(cmd, cwd=None, stdin=None, check=True, timeout=None):
    p = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=timeout)
    if check and p.returncode != 0:
        sys.exit("command failed (%d): %s\n%s" % (p.returncode, " ".join(cmd), p.stderr))
    return p


def gh_json(args):
    return json.loads(run(["gh"] + args).stdout)


def fetch_prs(repo, base, bot, since):
    q = "repo:%s is:pr author:%s base:%s" % (repo, bot, base)
    if since:
        q += " created:>=%s" % since
    prs, after = [], None
    while True:
        args = ["api", "graphql", "-f", "query=" + PR_QUERY, "-f", "q=" + q]
        if after:
            args += ["-f", "after=" + after]
        data = gh_json(args)["data"]["search"]
        prs += [n for n in data["nodes"] if n]
        if not data["pageInfo"]["hasNextPage"]:
            return prs
        after = data["pageInfo"]["endCursor"]


def bot_files(repo, pr, bot_names):
    """Return the paths the bot's own commits in the PR change.

    A person may push a fix to a bot branch; the files only that fix changes
    are theirs, not the bot's. Commits with several parents merge the base
    branch in and change nothing of their own, so they are skipped. The files
    of a single commit come from the REST API, fetched only for PRs that
    have a commit by someone else.
    """
    commits = [n["commit"] for n in pr["commits"]["nodes"] if n["commit"]["parents"]["totalCount"] < 2]

    def by_bot(c):
        user = (c["author"] or {}).get("user") or {}
        return (c["author"] or {}).get("name") in bot_names or user.get("login") in bot_names

    if all(by_bot(c) for c in commits) and pr["commits"]["totalCount"] <= 100:
        return [f["path"] for f in pr["files"]["nodes"]], False
    paths = set()
    for c in commits:
        if by_bot(c):
            paths |= set(gh_json(["api", "repos/%s/commits/%s" % (repo, c["oid"]),
                                  "--jq", "{f: [.files[].filename]}"])["f"])
    return sorted(paths), True


def classify(pr):
    """Return auto, manual, open-auto or open-manual."""
    # Renovate writes the automerge setting it applied into the PR body, so a PR
    # that someone merged before automerge fired still counts as automerged.
    renovate_auto = "**Automerge**: Enabled" in (pr.get("body") or "")
    if pr["state"] == "OPEN":
        return "open-auto" if pr["autoMergeRequest"] or renovate_auto else "open-manual"
    merged_by = pr["mergedBy"] or {}
    if pr["autoMergeRequest"] or renovate_auto or merged_by.get("__typename") == "Bot":
        return "auto"
    return "manual"


def is_major(pr):
    """Guess whether a PR is a major update from Renovate's table or Dependabot's title."""
    if re.search(r"\|\s*major\s*\|", pr.get("body") or "") or "(major)" in pr["title"] or \
            "renovate/major-" in pr["headRefName"]:
        return True
    m = re.search(r"from v?(\d+)\S* to v?(\d+)", pr["title"])
    return bool(m and m.group(1) != m.group(2))


def is_lfm(pr):
    return "lock-file-maintenance" in pr["headRefName"] or \
        pr["title"].lower().startswith("lock file maintenance") or \
        "lock file maintenance" in pr["title"].lower()


class Matcher:
    """Matches paths against single patterns with git's gitignore matcher.

    Each pattern is checked on its own: in a combined file git stops at an
    excluded parent directory, which CODEOWNERS does not do. A pattern ending
    in "/*" matches direct children only on GitHub, unlike in gitignore.
    """

    def __init__(self):
        self.dir = tempfile.mkdtemp(prefix="codeowners-match-")
        run(["git", "init", "-q", self.dir])
        self.cache = {}

    def match(self, pattern, paths):
        if not paths:
            return set()
        key = (pattern, tuple(paths))
        if key in self.cache:
            return self.cache[key]
        pat_file = os.path.join(self.dir, "pattern")
        with open(pat_file, "w") as f:
            f.write(pattern + "\n")
        # GitHub matches case-sensitively; git init on macOS sets ignoreCase.
        cmd = ["git", "-c", "core.excludesFile=" + pat_file, "-c", "core.ignoreCase=false",
               "check-ignore", "--no-index", "-z", "--stdin"]
        # One call takes milliseconds; a call once hung for ten minutes, so a
        # stuck one is killed and retried.
        for attempt in range(3):
            try:
                p = run(cmd, cwd=self.dir, stdin="\0".join(paths) + "\0", check=False,
                        timeout=60)
                break
            except subprocess.TimeoutExpired:
                if attempt == 2:
                    sys.exit("git check-ignore did not finish in 60 seconds for " + pattern)
        if p.returncode not in (0, 1):
            sys.exit("git check-ignore failed: " + p.stderr)
        hits = {x for x in p.stdout.split("\0") if x}
        if pattern.endswith("/*") and "**" not in pattern:
            depth = pattern.strip("/").count("/")
            hits = {h for h in hits if h.count("/") == depth}
        self.cache[key] = hits
        return hits


def parse_codeowners(text):
    """Return [(line_no, pattern, owners)] for rule lines."""
    rules = []
    for no, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = re.split(r"(?<!\\)\s+", s)
        owners = [o for o in parts[1:] if not o.startswith("#")]
        if "#" in parts[1:]:
            owners = owners[:[o.startswith("#") for o in parts[1:]].index(True)]
        rules.append((no, parts[0].replace("\\#", "#"), owners))
    return rules


def last_match(rules, matcher, paths):
    """Map each path to its last matching rule, or None."""
    result = {p: None for p in paths}
    for rule in rules:
        for hit in matcher.match(rule[1], paths):
            result[hit] = rule
    return result


def ignore_path_regex(pattern):
    """Translate a Renovate ignorePaths entry: a minimatch glob, or a plain
    path that matches as a substring."""
    if not any(c in pattern for c in "*?["):
        return re.compile(re.escape(pattern))
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + "$")


def verdict_of(path, automerged, keep, ownerless_source, ignore_res):
    """Return the verdict and its reason for a path a bot's commit changed."""
    if path in keep:
        return "keep", "--keep"
    if any(r.match(path) if r.pattern.endswith("$") else r.search(path) for r in ignore_res):
        return "ignored", "in Renovate ignorePaths"
    if SOURCE_FILE.search(path) and path not in ownerless_source:
        return "keep", "source code"
    return "ownerless", "automerged" if automerged else "merged by hand"


def pattern_sort_key(pattern):
    """Sort patterns by name, ignoring a leading / or *."""
    return pattern.lstrip("/*").lower()


def strip_block(text):
    """Return the lines of text without the generated block, and the number of
    lines before the block, or None when text has no block."""
    begin = BLOCK_BEGIN.split(":")[0]
    out, inside, at = [], False, None
    for line in text.splitlines():
        if line.strip().startswith(begin):
            inside = True
            if at is None:
                at = len(out)
        elif line.strip() == BLOCK_END and inside:
            inside = False
        elif not inside:
            out.append(line)
    if inside:
        raise ValueError("%s has no %s line after it; restore the line so the lines after "
                         "the block are not lost" % (begin, BLOCK_END))
    return out, at


def block_position(text):
    """Return the lines of text without the generated block, and the number of
    lines the block goes after. The block stays where it is, so a block the
    user moved by hand stays at its new place; a file without one gets it
    after the last * line, or at the end when no line is *."""
    lines, at = strip_block(text)
    if at is None:
        stars = [no for no, pattern, _ in parse_codeowners("\n".join(lines)) if pattern == "*"]
        at = stars[-1] if stars else len(lines)
    return lines, at


def replace_block(text, lines):
    """Replace the generated block in text with one that holds lines, or add
    it after the last * line, or at the end when no line is *, so the lines
    after it override the block."""
    out, at = block_position(text)
    head, tail = out[:at], out[at:]
    while head and not head[-1].strip():
        head.pop()
    while tail and not tail[0].strip():
        tail.pop(0)
    while tail and not tail[-1].strip():
        tail.pop()
    block = [BLOCK_BEGIN, BLOCK_COMMENT] + lines + [BLOCK_END]
    return "\n".join(head + ([""] if head else []) + block + ([""] + tail if tail else [])) + "\n"


def override_owners(text, matcher, paths):
    """Map each of paths to the owners an override line in the block must give
    it: those of its last matching line before the block. A path whose last
    matching line follows the block keeps its owners without an override, and
    one whose last matching line has no owners gets none. The generated block
    is left out, or a rerun would copy the owners of the previous run's
    override lines."""
    lines, at = block_position(text)
    found = last_match(parse_codeowners("\n".join(lines)), matcher, paths)
    return {p: rule[2] for p, rule in found.items() if rule and rule[2] and rule[0] <= at}


def check_verdicts(rows, current, text):
    """Return the paths whose last matching line in text disagrees with their
    verdict, and apart from them the ownerless paths that a line after the
    generated block keeps owned, as the block's placement intends."""
    ends = [no for no, line in enumerate(text.splitlines(), 1) if line.strip() == BLOCK_END]
    block_end = ends[-1] if ends else None
    mismatches, owned_after_block = [], []
    for path, r in rows.items():
        rule = current.get(path)
        owned = bool(rule and rule[2])
        if r["in_tree"] and r["verdict"] != "ignored" and owned != (r["verdict"] == "keep"):
            if owned and block_end and rule[0] > block_end:
                owned_after_block.append(path)
            else:
                mismatches.append(path)
    return mismatches, owned_after_block


def write_target(codeowners, repo_dir, co_path):
    """Return the file --write changes: the one --codeowners names, or the
    CODEOWNERS file of the clone, which must not be a symbolic link that could
    lead outside it."""
    if codeowners:
        return codeowners
    target = os.path.join(repo_dir, co_path)
    if os.path.islink(target):
        raise ValueError("%s is a symbolic link; pass the file to write with --codeowners" % target)
    return target


def proposed_pattern(path):
    for d in DIR_PATTERNS:
        if ("/" + path).startswith(d):
            return d
    base = path.rsplit("/", 1)[-1]
    if base in BASENAME_PATTERNS:
        return base
    for glob in ALWAYS:
        if "*" in glob and "/" not in glob and fnmatch.fnmatchcase(base, glob):
            return glob
    return "/" + path


def short(pr_or_commit):
    if "number" in pr_or_commit:
        oid = (pr_or_commit.get("mergeCommit") or {}).get("oid", "")
        return "#%d%s" % (pr_or_commit["number"], " " + oid[:8] if oid else "")
    return pr_or_commit["sha"][:8]


class LocalSource:
    """Reads the tree and files of origin/<base> in a clone."""

    def __init__(self, cwd, base):
        self.cwd = cwd
        self.ref = "origin/" + base
        if run(["git", "rev-parse", "--verify", "-q", self.ref], cwd=cwd, check=False).returncode:
            self.ref = base

    def tree(self):
        return [x for x in run(["git", "ls-tree", "-r", "--name-only", self.ref], cwd=self.cwd)
                .stdout.split("\n") if x]

    def show(self, path):
        p = run(["git", "show", "%s:%s" % (self.ref, path)], cwd=self.cwd, check=False)
        return p.stdout if p.returncode == 0 else None

    def workflows_mentioning(self, word):
        out = run(["git", "grep", "-l", word, self.ref, "--", ".github/workflows"],
                  cwd=self.cwd, check=False).stdout.split()
        return [x.split(":", 1)[-1] for x in out]

    def bot_commits(self, bots, pr_shas):
        """Commits a bot pushed straight to the base branch, as Renovate branch automerge does.

        First-parent history keeps out the commits of merged PR branches. A PR
        merged by rebase lands its commits on first-parent history with new
        SHAs, and all but the last are counted here; Renovate PRs have one
        commit, so this matters only for a PR a person pushed to.
        """
        log = run(["git", "log", "--first-parent", self.ref,
                   "--format=%x00%H%x09%an%x09%cs%x09%s", "--name-only"]
                  + ["--author=" + b.split("/")[-1] for b in bots], cwd=self.cwd).stdout
        commits = []
        for chunk in log.split("\0")[1:]:
            head, _, names = chunk.partition("\n")
            sha, author, date, subject = head.split("\t", 3)
            if "[bot]" not in author or sha in pr_shas or re.search(r"\(#\d+\)$", subject):
                continue
            commits.append({"sha": sha, "date": date, "subject": subject, "kind": "auto",
                            "major": False, "lfm": "lock file maintenance" in subject.lower(),
                            "paths": [n for n in names.split("\n") if n]})
        return commits


class RemoteSource:
    """Reads the tree and files of the base branch through the GitHub API."""

    def __init__(self, repo, base):
        self.repo, self.base = repo, base
        self.truncated = False

    def tree(self):
        data = gh_json(["api", "repos/%s/git/trees/%s?recursive=1" % (self.repo, self.base)])
        self.truncated = data["truncated"]
        self.paths = [e["path"] for e in data["tree"] if e["type"] == "blob"]
        return self.paths

    def show(self, path):
        p = run(["gh", "api", "-H", "Accept: application/vnd.github.raw",
                 "repos/%s/contents/%s?ref=%s" % (self.repo, path, self.base)], check=False)
        return p.stdout if p.returncode == 0 else None

    def workflows_mentioning(self, word):
        return [t for t in self.paths if t.startswith(".github/workflows/")
                and word in (self.show(t) or "")]

    def bot_commits(self, bots, pr_shas):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo-dir", help="a fetched clone; default: the GitHub API when --repo "
                                        "is given, else the current directory")
    ap.add_argument("--repo", help="owner/name; default: gh repo view")
    ap.add_argument("--base", help="base branch; default: the repository default")
    ap.add_argument("--bot", action="append",
                    help="PR author for GitHub search, repeatable; "
                         "default: app/renovate and app/dependabot")
    ap.add_argument("--since", help="only PRs created on or after YYYY-MM-DD")
    ap.add_argument("--codeowners", help="check this file instead of the one on the base branch")
    ap.add_argument("--keep", action="append", default=[],
                    help="path that must keep its owners, such as a file a packageRules "
                         "entry excludes from automerge; repeatable")
    ap.add_argument("--ownerless-source", action="append", default=[],
                    help="source file a bot changed that goes ownerless all the same; repeatable")
    ap.add_argument("--examples", type=int, default=3,
                    help="list every PR for a row changed this many times or fewer")
    ap.add_argument("--all", action="store_true", help="also list paths deleted from the tree")
    ap.add_argument("--write", action="store_true",
                    help="replace the generated block in the CODEOWNERS file of --repo-dir, or in "
                         "--codeowners, and check the result")
    ap.add_argument("--json", action="store_true", help="print JSON instead of Markdown")
    a = ap.parse_args()

    cwd = a.repo_dir or (None if a.repo else ".")
    repo = a.repo or json.loads(run(["gh", "repo", "view", "--json", "nameWithOwner"],
                                    cwd=cwd).stdout)["nameWithOwner"]
    base = a.base or gh_json(["api", "repos/" + repo, "--jq", "{b: .default_branch}"])["b"]
    src = LocalSource(cwd, base) if cwd else RemoteSource(repo, base)
    bots = a.bot or ["app/renovate", "app/dependabot"]

    prs = []
    for bot in bots:
        prs += [p for p in fetch_prs(repo, base, bot, a.since) if p["state"] in ("MERGED", "OPEN")]
    # app/renovate searches PRs by the app; its commits carry renovate[bot].
    bot_names = {b.split("/", 1)[-1] + "[bot]" for b in bots} | {b.split("/", 1)[-1] for b in bots}
    for p in prs:
        p["bot_files"], p["mixed"] = bot_files(repo, p, bot_names)
        p["kind"] = classify(p)
        p["lfm"] = is_lfm(p)
        p["major"] = is_major(p)
        p.pop("body", None)
    pr_shas = {(p.get("mergeCommit") or {}).get("oid") for p in prs}

    commits = src.bot_commits(bots, pr_shas)
    tree = src.tree()
    tree_set = set(tree)
    basenames = {t.rsplit("/", 1)[-1] for t in tree}

    # Per-path history.
    hist = defaultdict(lambda: defaultdict(list))
    truncated = []
    for p in prs:
        if p["files"]["totalCount"] > len(p["files"]["nodes"]):
            truncated.append(p["number"])
        for path in p["bot_files"]:
            hist[path][p["kind"]].append(p)
    for c in commits or ():
        for path in c["paths"]:
            hist[path]["auto"].append(c)

    def date_of(x):
        return x.get("mergedAt") or x.get("createdAt") or x.get("date") or ""

    first_auto = min([date_of(x) for x in prs + (commits or []) if x["kind"] == "auto"] or [""])
    if not first_auto:
        sys.exit("%s: none of the %d bot PRs on %s was automerged, so every one of them needs "
                 "its review request; enable automerge first" % (repo, len(prs), base))

    # Current or given CODEOWNERS.
    co_path, co_text = a.codeowners, None
    if a.codeowners:
        with open(a.codeowners) as f:
            co_text = f.read()
    else:
        for loc in CODEOWNERS_LOCATIONS:
            text = src.show(loc) if loc in tree else None
            if text is not None:
                co_path, co_text = loc, text
                break
    rules = parse_codeowners(co_text or "")
    matcher = Matcher()

    # Verdicts. Every path a bot's own commit changed goes ownerless, however
    # its PR was merged: a bot PR merged by hand is one automerge did not
    # finish, and nobody wants a review request for it. Source code keeps its
    # owners even then: a bot changes it only to rewrite imports on a major
    # update, and people's PRs to it need review. So do the paths a Renovate
    # rule excludes from automerge, given as --keep.
    # A path the Renovate configuration now ignores gets no more bot PRs.
    # JSON5 configurations are not parsed, so their ignorePaths stay unread.
    ignore_paths, renovate_config = [], None
    for loc in RENOVATE_LOCATIONS:
        text = src.show(loc) if loc in tree_set else None
        if text is not None:
            renovate_config = loc
            try:
                ignore_paths = json.loads(text).get("ignorePaths", [])
            except ValueError:
                renovate_config += " (not JSON, ignorePaths unread)"
            break
    ignore_res = [ignore_path_regex(x) for x in ignore_paths]
    keep = {k.lstrip("/") for k in a.keep}
    ownerless_source = {k.lstrip("/") for k in a.ownerless_source}
    rows = {}
    for path, kinds in hist.items():
        auto = kinds["auto"] + kinds["open-auto"]
        manual = kinds["manual"] + kinds["open-manual"]
        verdict, reason = verdict_of(path, bool(auto), keep, ownerless_source, ignore_res)
        rows[path] = {"path": path, "verdict": verdict, "reason": reason,
                      "in_tree": path in tree_set, "auto": auto, "manual": manual}

    keep_paths = sorted({p for p, r in rows.items() if r["verdict"] == "keep" and r["in_tree"]}
                        | keep)

    # Proposed patterns: generalise ownerless paths and add well-known ones. A
    # path that must keep its owners but matches a proposed pattern keeps them
    # through a line after the block, if it has one. Otherwise, it gets an
    # override line after the patterns, so the pattern still covers future
    # files (override_owners). A path whose last matching line has no owners
    # gets none, and the check below reports it.
    lfm_manual = [p for p in prs if p["lfm"] and p["kind"] in ("manual", "open-manual")]
    candidates = defaultdict(lambda: {"sources": set(), "paths": []})
    ownerless = {p for p, r in rows.items() if r["verdict"] == "ownerless" and r["in_tree"]}
    by_name = defaultdict(set)
    for t in tree:
        by_name[t.rsplit("/", 1)[-1]].add(t)
    for r in rows.values():
        if r["path"] in ownerless:
            pat = proposed_pattern(r["path"])
            name = r["path"].rsplit("/", 1)[-1]
            # A file name whose every copy bots update stands for its future
            # copies too; source code always stays anchored to its path.
            if pat.startswith("/") and len(by_name[name]) > 1 and by_name[name] <= ownerless \
                    and not SOURCE_FILE.search(name):
                pat = name
            candidates[pat]["sources"].add("history")
            candidates[pat]["paths"].append(r["path"])
    for pat in ALWAYS:
        candidates[pat]["sources"].add("always")
        candidates[pat]["keep_unmatched"] = True
    for eco in ECOSYSTEMS:
        if not basenames.intersection(eco["detect"]):
            continue
        for pat in eco["patterns"]:
            candidates[pat]["sources"].add("ecosystem:" + eco["name"])
            candidates[pat]["keep_unmatched"] = True
        for pat in eco.get("lfm", []):
            candidates[pat]["sources"].add("ecosystem:" + eco["name"])

    proposals, reached = [], set()
    for pat, c in candidates.items():
        tree_hits = matcher.match(pat, tree)
        # A pattern of a detected ecosystem stays without a match, so a file
        # added later is covered; a lock file stays only where one exists.
        if not c["paths"] and not tree_hits and not c.get("keep_unmatched"):
            continue
        reached |= matcher.match(pat, keep_paths)
        proposals.append({"pattern": pat, "sources": sorted(c["sources"]),
                          "paths": sorted(c["paths"]),
                          "tree_matches": len(tree_hits),
                          "tree_untouched": sorted(tree_hits - set(rows))[:5]})
    proposals.sort(key=lambda x: pattern_sort_key(x["pattern"]))
    try:
        overrides = override_owners(co_text or "", matcher, sorted(reached))
    except ValueError as e:
        sys.exit("%s: %s" % (co_path, e))

    if a.write:
        if co_path is None:
            sys.exit("%s has no CODEOWNERS file, so no bot PR requests review" % repo)
        if not a.codeowners and not a.repo_dir:
            sys.exit("--write needs --repo-dir or --codeowners")
        try:
            target = write_target(a.codeowners, a.repo_dir, co_path)
        except ValueError as e:
            sys.exit(str(e))
        with open(target) as f:
            old_text = f.read()
        try:
            co_text = replace_block(old_text, [pr["pattern"] for pr in proposals] +
                                    ["/%s %s" % (k, " ".join(o)) for k, o in sorted(overrides.items())])
        except ValueError as e:
            sys.exit("%s: %s" % (target, e))
        with open(target, "w") as f:
            f.write(co_text)
        co_path = target
        rules = parse_codeowners(co_text)

    current = last_match(rules, matcher, sorted(rows)) if rules else {}
    for path, r in rows.items():
        rule = current.get(path)
        r["current"] = None if not rule else {"line": rule[0], "pattern": rule[1],
                                               "owners": rule[2]}
    mismatches, owned_after_block = check_verdicts(rows, current, co_text or "")

    # Rulesets and classic branch protection both apply, so either one can
    # require code-owner review.
    rulesets = run(["gh", "api", "repos/%s/rules/branches/%s" % (repo, base)], check=False)
    by_ruleset = rulesets.returncode == 0 and any(
        rule.get("type") == "pull_request" and rule["parameters"].get("require_code_owner_review")
        for rule in json.loads(rulesets.stdout))
    prot = run(["gh", "api", "repos/%s/branches/%s/protection" % (repo, base)], check=False)
    if prot.returncode == 0:
        by_classic = bool(json.loads(prot.stdout).get("required_pull_request_reviews", {})
                          .get("require_code_owner_reviews"))
    elif "Branch not protected" in prot.stdout + prot.stderr:
        by_classic = False
    else:
        by_classic = None
    if rulesets.returncode != 0:
        code_owner_review = "unknown: rulesets unreadable"
    elif by_ruleset or by_classic:
        code_owner_review = True
    elif by_classic is None:
        code_owner_review = "unknown: no ruleset requires it, classic protection unreadable"
    else:
        code_owner_review = False
    pr_assigner = src.workflows_mentioning("pr-assigner")
    # pr-assigner (Netcracker/qubership-workflow-hub) assigns the owners of the
    # first line that starts with "*", or of the last line when none does.
    assigner_warnings = []
    if pr_assigner:
        star = [r for r in rules if r[1].startswith("*")]
        if not star:
            assigner_warnings.append("no line starts with *: pr-assigner reads the last line, "
                                     "which the ownerless block must not be")
        elif star[0][1] != "*":
            assigner_warnings.append("pr-assigner reads L%d `%s`, not the * line"
                                     % (star[0][0], star[0][1]))

    counts = defaultdict(int)
    for p in prs:
        counts[p["kind"]] += 1
    summary = {
        "repo": repo, "base": base, "bots": bots, "codeowners": co_path,
        "prs": dict(counts),
        "branch_commits": "not checked: needs --repo-dir" if commits is None else len(commits),
        "tree_truncated": getattr(src, "truncated", False),
        "first_automerge": first_auto,
        "lock_file_maintenance": {"by_hand": [short(p) for p in lfm_manual],
                                  "turn_on_automerge": bool(lfm_manual),
                                  "automerged": [short(p) for p in prs
                                                 if p["lfm"] and p["kind"] == "auto"]},
        "renovate_config": renovate_config,
        "renovate_ignore_paths": ignore_paths,
        "ruleset_requires_code_owner_review": code_owner_review,
        "pr_assigner_workflows": pr_assigner,
        "pr_assigner_warnings": assigner_warnings,
        "prs_with_over_100_files": truncated,
        "prs_with_commits_by_others": [short(p) for p in prs if p["mixed"]],
    }

    if a.json:
        def slim(xs):
            return [short(x) for x in sorted(xs, key=date_of, reverse=True)]
        out = {"summary": summary, "proposals": proposals, "overrides": overrides,
               "paths": [dict(r, auto=slim(r["auto"]), manual=slim(r["manual"]))
                         for r in sorted(rows.values(), key=lambda r: r["path"])],
               "mismatches": sorted(mismatches), "owned_after_block": sorted(owned_after_block)}
        json.dump(out, sys.stdout, indent=1)
        print()
        return

    def ex(xs):
        xs = sorted(xs, key=date_of, reverse=True)
        if not xs:
            return ""
        if len(xs) <= a.examples:
            return ", ".join(short(x) for x in xs)
        return "%d, last %s" % (len(xs), short(xs[0]))

    print("# Bot-updated paths in %s (%s)\n" % (repo, base))
    for k, v in summary.items():
        print("- %s: %s" % (k, json.dumps(v)))
    print("\n## Paths bots changed\n")
    print("| verdict | path | automerged | by hand | current last match | |")
    print("|---|---|---|---|---|---|")
    for r in sorted(rows.values(), key=lambda r: (r["verdict"], r["path"])):
        if not r["in_tree"] and not a.all:
            continue
        cur = r["current"]
        cur_s = "-" if not cur else "L%d `%s` %s" % (cur["line"], cur["pattern"],
                                                    " ".join(cur["owners"]) or "(none)")
        flag = " ".join(f for f, on in (("deleted", not r["in_tree"]),
                                        ("MISMATCH", r["path"] in mismatches)) if on)
        print("| %s (%s) | `%s` | %s | %s | %s | %s |" % (
            r["verdict"], r["reason"], r["path"], ex(r["auto"]), ex(r["manual"]), cur_s, flag))
    print("\n## Proposed ownerless patterns\n")
    print("| pattern | sources | bot paths | tree matches | untouched by bots (first 5) |")
    print("|---|---|---|---|---|")
    for pr in proposals:
        print("| `%s` | %s | %s | %s | %s |" % (
            pr["pattern"], ", ".join(pr["sources"]), len(pr["paths"]),
            pr.get("tree_matches", ""), " ".join("`%s`" % x for x in pr.get("tree_untouched", []))))
    print("\n## Proposed CODEOWNERS block\n")
    print("```text")
    for pr in proposals:
        print(pr["pattern"])
    for k, owners in sorted(overrides.items()):
        print("/%s %s" % (k, " ".join(owners)))
    print("```")
    print("\n## Paths whose last matching line in %s disagrees with the verdict\n"
          % (co_path or "CODEOWNERS"))
    print("\n".join("- `%s`" % m for m in sorted(mismatches)) or "none")
    print("\n## Bot-updated paths a line after the block keeps owned\n")
    print("\n".join("- `%s` (L%d `%s`)" % (m, rows[m]["current"]["line"], rows[m]["current"]["pattern"])
                    for m in sorted(owned_after_block)) or "none")


if __name__ == "__main__":
    main()
