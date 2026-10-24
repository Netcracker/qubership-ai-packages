"""Fetches, for every PR in dataset/prs.json, the diff of the initial and the final version at the pinned SHAs, and
the review thread; writes cache/dossiers/<key>.json (classifier input) and cache/views/<key>.* (labeler input).

Needs an authenticated `gh`. The initial SHA was chosen once, when the dataset was built: the head before the first
force-push after the first non-author, non-bot feedback, or the last commit before that feedback, or the final head
when there was no feedback; apache/calcite#5278, still open, was set by hand. dataset/prs.json records which rule
applied as `initial_how`. The title and description are fetched as they are now.
"""
import json
import os
import subprocess
import sys
import time

from common import CACHE, prs


def gh(api_path, accept=None, paginate=True):
    cmd = ["gh", "api"] + (["--paginate"] if paginate else []) + (["-H", f"Accept: {accept}"] if accept else []) + [api_path]
    for attempt in range(4):          # GitHub answers 502 now and then
        r = subprocess.run(cmd, capture_output=True, text=True)
        if not r.returncode:
            return r.stdout
        time.sleep(2 ** attempt)
    raise RuntimeError(f"{api_path}: {r.stderr[:200]}")


def ghj(api_path, paginate=True):
    out = gh(api_path, paginate=paginate).strip()
    return json.loads(out.replace("]\n[", ",").replace("][", ",")) if out else []


def fetch(p):
    repo, num = p["repo"], p["number"]
    pr = ghj(f"repos/{repo}/pulls/{num}", paginate=False)
    cmp = ghj(f"repos/{repo}/compare/{p['base_sha']}...{p['initial_sha']}", paginate=False)
    diff = lambda sha: gh(f"repos/{repo}/compare/{p['base_sha']}...{sha}", accept="application/vnd.github.diff", paginate=False)
    initial = diff(p["initial_sha"])
    return {"repo": repo, "number": num, "title": pr["title"], "body": pr["body"] or "", "author": pr["user"]["login"],
            "files": [(f["filename"], f["additions"], f["deletions"]) for f in cmp["files"]],
            "initial_diff": initial, "final_diff": initial if p["final_sha"] == p["initial_sha"] else diff(p["final_sha"]),
            "commits": [{"sha": c["sha"][:10], "date": c["commit"]["committer"]["date"], "message": c["commit"]["message"]}
                        for c in ghj(f"repos/{repo}/pulls/{num}/commits")],
            "reviews": [{"user": (x["user"] or {}).get("login"), "state": x["state"], "at": x.get("submitted_at"), "body": x["body"]}
                        for x in ghj(f"repos/{repo}/pulls/{num}/reviews")],
            "review_comments": [{"user": x["user"]["login"], "at": x["created_at"], "path": x["path"], "body": x["body"]}
                                for x in ghj(f"repos/{repo}/pulls/{num}/comments")],
            "issue_comments": [{"user": x["user"]["login"], "at": x["created_at"], "body": x["body"]}
                               for x in ghj(f"repos/{repo}/issues/{num}/comments")]}


def view(p, d):
    """The labeler's reading copy: the thread as Markdown and both diffs as files."""
    base = os.path.join(CACHE, "views", p["key"])
    open(base + ".initial.diff", "w").write(d["initial_diff"])
    open(base + ".final.diff", "w").write(d["final_diff"])
    lines = [f"# {p['repo']}#{p['number']}: {d['title']}", "",
             f"Author: {d['author']}; base {p['base_sha'][:10]}; initial {p['initial_sha'][:10]} ({p['initial_how']}); "
             f"final {p['final_sha'][:10]}", "", "## Description", "", d["body"] or "(empty)", "",
             "## Files in the initial version", ""]
    lines += [f"- {f} (+{a} -{b})" for f, a, b in d["files"]]
    lines += ["", "## Commits", ""] + [f"- {c['sha']} {c['date']}: {c['message'][:600]}" for c in d["commits"]]
    lines += ["", "## Reviews", ""] + [f"- {r['user']} {r['state']} {r['at']}: {r['body'][:2000]}" for r in d["reviews"] if r["body"]]
    lines += ["", "## Inline review comments", ""] + [f"- {r['user']} {r['at']} on `{r['path']}`: {r['body'][:1500]}"
                                                       for r in d["review_comments"]]
    lines += ["", "## Conversation comments", ""] + [f"- {r['user']} {r['at']}: {r['body'][:1500]}" for r in d["issue_comments"]]
    open(base + ".md", "w").write("\n".join(lines))


if __name__ == "__main__":
    os.makedirs(os.path.join(CACHE, "dossiers"), exist_ok=True)
    os.makedirs(os.path.join(CACHE, "views"), exist_ok=True)
    for p in prs():
        out = os.path.join(CACHE, "dossiers", f"{p['key']}.json")
        if not os.path.exists(out):
            json.dump(fetch(p), open(out, "w"), indent=1)
            print("fetched", p["key"], file=sys.stderr)
        view(p, json.load(open(out)))
