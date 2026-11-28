"""Paths, the axis list, and the classifier input shared by every script in this directory."""
import json
import os
import threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "cache")          # fetched diffs and review threads; not committed
AXES = ["tests", "user_docs", "doc_comments", "change_description", "performance", "security", "backward_compat",
        "concurrency", "error_model", "correctness", "user_value", "surprising_behavior", "contradictions",
        "build_ci", "observability", "spec_conformance"]
MAX_FILES = 80


def path(*parts):
    return os.path.join(ROOT, *parts)


def prs():
    return json.load(open(path("dataset", "prs.json")))


def keys():
    return [p["key"] for p in prs()]


def profiles():
    return json.load(open(path("dataset", "profiles.json")))


def dossier(key):
    f = os.path.join(CACHE, "dossiers", f"{key}.json")
    if not os.path.exists(f):
        raise SystemExit(f"{f} is missing: run scripts/fetch_inputs.py first")
    return json.load(open(f))


def pr_input(key, diff_chars):
    """What a reviewer sees when the pull request is opened: title, description, files, and the diff of the
    initial version cut to ``diff_chars`` characters (none when 0). The files and the diff are those of the initial
    version; the title and description are the pull request's current ones, which an author may have edited during
    review."""
    d = dossier(key)
    files = sorted(d["files"], key=lambda f: -(f[1] + f[2]))
    shown = [f"{p} (+{a} -{b})" for p, a, b in files[:MAX_FILES]]
    if len(files) > MAX_FILES:
        shown.append(f"... and {len(files) - MAX_FILES} more files")
    out = {"repository": d["repo"], "title": d["title"], "description": (d["body"] or "")[:4000],
           "shortstat": f"{len(files)} files changed, +{sum(f[1] for f in files)} -{sum(f[2] for f in files)}",
           "files": shown}
    if diff_chars:
        diff = d["initial_diff"]
        out["diff"] = diff[:diff_chars] + (f"\n... diff truncated, {len(diff) - diff_chars} more characters"
                                           if len(diff) > diff_chars else "")
    return out


def compact(x, digits=6):
    """Rounds every float to ``digits`` decimals, so that a probability is stored as 0.9999, not 0.9999769571498561.
    A cost keeps 8 decimals: a Jev call costs about $0.0002."""
    if isinstance(x, float):
        return round(x, digits)
    if isinstance(x, dict):
        return {k: compact(v, 8 if k.startswith("cost") else digits) for k, v in x.items()}
    if isinstance(x, list):
        return [compact(v, digits) for v in x]
    return x


class Preds:
    """The predictions of one classifier: preds/<classifier>.jsonl, one compact JSON object per PR, sorted by key.

    ``put`` rewrites the file after every prediction, so an interrupted run keeps what it has and a rerun asks only
    for the PRs still missing. Safe to call from several threads."""

    def __init__(self, classifier):
        self.file = path("preds", f"{classifier}.jsonl")
        self.rows = load_preds(classifier) if os.path.exists(self.file) else {}
        self.lock = threading.Lock()

    def __contains__(self, key):
        return key in self.rows

    def __getitem__(self, key):
        return self.rows[key]

    def put(self, pred):
        with self.lock:
            self.rows[pred["key"]] = compact(pred)
            os.makedirs(os.path.dirname(self.file), exist_ok=True)
            with open(self.file, "w") as f:
                for k in sorted(self.rows):
                    f.write(json.dumps(self.rows[k], separators=(",", ":"), ensure_ascii=False) + "\n")


def load_preds(classifier):
    """{PR key: prediction} from preds/<classifier>.jsonl."""
    with open(path("preds", f"{classifier}.jsonl")) as f:
        return {r["key"]: r for r in (json.loads(line) for line in f if line.strip())}
