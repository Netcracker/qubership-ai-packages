"""A free baseline: path and keyword rules, no model. p_required is the rule's label mapped to 0, 0.4, 0.9.

Usage: python3 classify_heuristic.py        -> preds/heuristic.jsonl
"""
import re

from common import AXES, Preds, keys, pr_input

TEST = re.compile(r"(^|/)(src/test|test|tests|testFixtures)/|Test[s]?\.java$|\.q$|\.iq$")
DOCS = re.compile(r"(^|/)(docs?|site)/|\.md$|\.adoc$|\.po$")
BUILD = re.compile(r"(^|/)(\.github/|build\.gradle|settings\.gradle|gradle/|buildSrc|build-logic|pom\.xml|renovate|\.gradle\.kts$|gradle\.properties)")


def kw(text, words):
    return re.search(r"\b(" + words + r")", text, re.I) is not None


def classify(key):
    x = pr_input(key, 0)
    text = x["title"] + "\n" + x["description"]
    files = [f.split(" (+")[0] for f in x["files"]]
    main = [f for f in files if f.endswith((".java", ".kt", ".scala")) and not TEST.search(f) and not BUILD.search(f)]
    tests_ = [f for f in files if TEST.search(f)]
    docs = [f for f in files if DOCS.search(f)]
    build = [f for f in files if BUILD.search(f)]
    lines = sum(int(m.group(1)) + int(m.group(2)) for f in x["files"] if (m := re.search(r"\(\+(\d+) -(\d+)\)", f)))
    m = bool(main)
    L = {
        "tests": 2 if m else (1 if tests_ else 0),
        "user_docs": 2 if kw(text, "option|property|propert|parameter|jdk|java \\d|toolchain|deprecat|default|flag|config") else (1 if docs else 0),
        "doc_comments": 2 if m and lines > 150 else (1 if m else 0),
        "change_description": 2 if m and kw(text, "feat|add|support|fix") else (1 if m else 0),
        "performance": 2 if kw(text, "perf|fast|slow|optimi|benchmark|buffer|cache|alloc|batch|join|speed") else (1 if m else 0),
        "security": 2 if kw(text + " ".join(files), "auth|scram|ssl|tls|password|token|secret|escap|quot|inject|security|cve|untrusted|length|bound") else 0,
        "backward_compat": 2 if kw(text, "remov|deprecat|default|renam|drop|break|jdk|upgrad|compat|migrat") else (1 if m else 0),
        "concurrency": 2 if kw(text, "thread|lock|concurr|close|leak|stream|flush|synchron|race") else 0,
        "error_model": 2 if kw(text, "error|exception|throw|reject|fail") else (1 if m else 0),
        "correctness": 2 if m and lines > 20 else (1 if m else 0),
        "user_value": 2 if kw(x["title"], "feat|add|support|introduc|implement") else (1 if m else 0),
        "surprising_behavior": 2 if kw(text, "default|silent|behavio|implicit") else (1 if m else 0),
        "contradictions": 2 if docs and m else (1 if docs or m else 0),
        "build_ci": 2 if build else 0,
        "observability": 2 if kw(text, "log|metric|trac|warn") else 0,
        "spec_conformance": 2 if kw(text, "spec|standard|jspecify|protocol|jdbc|sql:\\d") else 0,
    }
    plan = "split" if sum(v == 2 for v in L.values()) >= 6 or lines > 800 else "single"
    return {"key": key, "axes": {a: {"label": L[a], "p_required": [0, 0.4, 0.9][L[a]]} for a in AXES},
            "plan": {"mode": plan}, "cost_usd": 0.0, "latency_s": 0.0}


if __name__ == "__main__":
    out = Preds("heuristic")
    for k in keys():
        out.put(classify(k))
