"""The typed questions asked of System One models (Jev, CLM): one per axis, either a 0-2 score or a yes/no (noul),
plus whether the review should be split."""
from common import AXES

AXIS_TEXT = {
    "tests": ("the tests", "Does the change owe tests (new behavior or a bug fix), or are the tests it adds weak, missing a regression or negative case, or unable to fail?"),
    "user_docs": ("the user documentation", "Does the change add, rename, remove or change something users read about in docs (an option, property, flag, supported JDK/database/Gradle version, a user-visible error or behavior), so that docs pages, README, or migration notes must be updated?"),
    "doc_comments": ("the Javadoc and code comments", "Does the change add or change a public contract or non-obvious code whose Javadoc or comments must be written or updated, or do the comments risk disagreeing with the code?"),
    "change_description": ("the PR description, commit message and changelog", "Does the change owe a changelog or release-note entry, or does its title/description fail to say what changes and why?"),
    "performance": ("performance", "Does the change touch a hot path, an allocation- or IO-heavy loop, algorithmic complexity, or claim a speed-up, so that a benchmark or measurement is owed?"),
    "security": ("security", "Does the change touch authentication, TLS, crypto, credentials, parsing of untrusted network input, quoting/escaping, or resource exhaustion?"),
    "backward_compat": ("backward compatibility", "Could the change break existing users: public API/ABI, a default, a supported platform or version, persisted or wire formats, or behavior users rely on?"),
    "concurrency": ("concurrency and resource lifecycle", "Does the change touch shared state, locking, threads, or opening and closing of streams, connections, or other resources?"),
    "error_model": ("the error model", "Does the change add or change what is thrown or returned on failure, error messages, error codes, or diagnostics?"),
    "correctness": ("logic correctness and edge cases", "Does the change add or modify non-trivial logic where boundary cases (null, empty, off-by-one, unusual inputs) could be wrong?"),
    "user_value": ("usefulness to users", "Does the change add a feature, option, or user-facing API whose usefulness, API shape, or UX deserves scrutiny?"),
    "surprising_behavior": ("surprising behavior", "Could the change introduce behavior a user would not expect: silent changes, hidden side effects, swallowed errors?"),
    "contradictions": ("contradictions", "Could the change introduce a contradiction: code vs docs, comments, tests or the PR description; with similar code elsewhere; or within itself?"),
    "build_ci": ("build, CI and dependencies", "Does the change modify build scripts, CI configuration, dependency versions, packaging, or release?"),
    "observability": ("logging, metrics and tracing", "Does the change add a failure, retry, fallback, or state that should be logged or measured, or change existing logging?"),
    "spec_conformance": ("conformance to an external specification", "Does the change implement or interpret an external spec (SQL standard, PostgreSQL protocol, JDBC spec, JSpecify, Java language spec) where it could deviate?"),
}

PLAN_SPLIT = {"type": "noul", "instructions": "Is the pull request described in `pr` large or diverse enough that its review should be split across several focused reviewers, each covering a few review aspects, rather than done by a single reviewer?",
              "criteria": {"true": "Split: large, touches several unrelated concerns", "false": "Single reviewer: small or cohesive change"}}


def score_questions():
    q = {}
    for a in AXES:
        area, detail = AXIS_TEXT[a]
        q[a] = {"type": "score",
                "instructions": f"How much review attention does the pull request described in `pr` need on {area}? {detail}",
                "criteria": [f"0 skip: the change does not touch {area}",
                             f"1 glance: {area} is touched, but a quick look is enough; a focused review would find nothing",
                             f"2 required: a focused review of {area} is owed, because the kind of change requires it or the pull request likely has a defect or omission there"]}
    q["plan_split"] = PLAN_SPLIT
    return q


def noul_questions():
    q = {}
    for a in AXES:
        area, detail = AXIS_TEXT[a]
        q[a] = {"type": "noul", "instructions": f"Does the pull request described in `pr` need a focused review of {area}? {detail}",
                "criteria": {"true": f"Yes: the kind of change requires a check of {area}, or the pull request likely has a defect or omission there",
                             "false": f"No: {area} is untouched, or a quick glance is enough"}}
    q["plan_split"] = PLAN_SPLIT
    return q


def to_pred(key, answers, noul):
    """Maps typed answers to the prediction shape report.py reads: per-axis P(label) and the split probability."""
    if noul:
        axes = {x: {"score": 2 * answers[x]["noul"], "p": {"0": 1 - answers[x]["noul"], "1": 0.0, "2": answers[x]["noul"]}} for x in AXES}
    else:
        axes = {x: {"score": answers[x]["score"], "p": answers[x]["probabilities"]} for x in AXES}
    return {"key": key, "axes": axes, "plan_split": answers["plan_split"]["noul"]}


def variant_spec(variant):
    """'profile-noul-diff8k' -> (with profile, noul questions, 8000 diff characters)."""
    parts = variant.split("-")
    return "profile" in parts, "noul" in parts, {"meta": 0, "diff4k": 4000, "diff8k": 8000, "diff24k": 24000}[parts[-1]]
