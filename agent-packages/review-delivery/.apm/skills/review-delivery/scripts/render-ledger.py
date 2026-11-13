#!/usr/bin/env python3
"""Render a review.json as ledger.md, in English, with no model in the loop.

Usage: render-ledger.py <review.json> [<ledger.md>]

Writes the ledger next to review.json unless an output path is given. Exits with status 2, naming the field, where a
field the ledger reads is missing or has a value the schema does not allow; it is not a full schema validator.
"""
import json
import os
import re
import sys

SEVERITIES = ("major", "minor", "nit")
ORIGINS = ("change", "stack", "preexisting")
OPEN_PREVIOUS = ("fix_not_accepted",)


def fail(message):
    print(f"render-ledger: {message}", file=sys.stderr)
    sys.exit(2)


def check(review):
    for key in ("schema_version", "target", "revision", "result", "findings"):
        if key not in review:
            fail(f"missing top-level field '{key}'")
    if review["result"] not in ("approve", "request_changes", "review_incomplete"):
        fail(f"result: unknown value '{review['result']}'")
    if review["result"] == "review_incomplete" and not review.get("coverage_gap"):
        fail("coverage_gap: required when result is review_incomplete")
    for n, f in enumerate(review["findings"]):
        for key in ("id", "title", "kind", "severity", "confidence", "axis", "location", "problem",
                    "proposed_solution"):
            if key not in f:
                fail(f"findings[{n}]: missing '{key}'")
        if f["severity"] not in SEVERITIES:
            fail(f"findings[{n}].severity: unknown value '{f['severity']}'")
        if f.get("gate", "none") not in ("none", "code_settled"):
            fail(f"findings[{n}].gate: unknown value '{f['gate']}'")
        if origin(f) not in ORIGINS:
            fail(f"findings[{n}].origin: unknown value '{f['origin']}'")
        if origin(f) == "stack" and not (f.get("introduced_by") or {}).get("request"):
            fail(f"findings[{n}].introduced_by.request: required for a stack finding")
        if origin(f) == "preexisting" and f.get("disposition") not in ("extend_scope", "follow_up"):
            fail(f"findings[{n}].disposition: required for a preexisting finding")


def origin(f):
    return f.get("origin", "change")


def own(review):
    """Return the findings the change makes: only they count in the result and hold the branch requests."""
    return [f for f in review["findings"] if origin(f) == "change"]


def result_line(review):
    if review["result"] == "review_incomplete":
        return f"Result: REVIEW_INCOMPLETE\nCoverage: {review['coverage_gap']}"
    counts = {s: sum(1 for f in own(review) if f["severity"] == s) for s in SEVERITIES}
    return (f"Result: {review['result'].upper()} "
            f"({counts['major']} major, {counts['minor']} minor, {counts['nit']} nit)")


def location(f):
    loc = f["location"]
    if loc is None:
        return "no line"
    lines = str(loc["start_line"])
    if loc.get("end_line") and loc["end_line"] != loc["start_line"]:
        lines += f"-{loc['end_line']}"
    text = f"`{loc['path']}:{lines}`"
    if loc["side"] == "old":
        text += " (removed line)"
    if loc.get("in_diff") is False:
        text += " (outside the diff)"
    return text


def finding(f):
    kind = " (question)" if f["kind"] == "question" else ""
    older = ", pre-existing" if origin(f) == "preexisting" else ""
    out = [f"### {f['id']} {f['severity']}{older}: {f['title']}{kind} ({f['axis']})", "",
           f"{location(f)} · Confidence: {f['confidence']}", "",
           f"- Problem: {f['problem']}"]
    for e in f.get("evidence", []):
        out.append(f"  - {e['basis']}: {e['text']}")
    out.append(f"- Proposed solution: {f['proposed_solution']}")
    if f.get("prior_thread"):
        out.append(f"- Continues: {f['prior_thread']}")
    by = f.get("introduced_by") or {}
    if by.get("request") or by.get("commit"):
        out.append(f"- Introduced by: {', '.join(v for v in (by.get('request'), by.get('commit')) if v)}")
    if origin(f) == "preexisting":
        out.append(f"- Disposition: {f['disposition']}")
        out.append(f"- Follow-up: {f.get('follow_up_url') or 'not filed'}")
    out.append("")
    return out


def held(review):
    """Return the findings held until the code is settled, by the rule in SKILL.md."""
    # An extend_scope finding asks for a code change in this change too, so it keeps the branch requests waiting.
    open_code = any(f.get("gate", "none") == "none" and f["severity"] in ("major", "minor")
                    for f in review["findings"] if in_classes(f))
    # A thread that continues as a finding of this file counts at that finding's severity, in the check above. One
    # without such a finding has no severity here, so it holds the branch requests whatever its severity was.
    ids = {f["id"] for f in review["findings"]}
    open_code = open_code or any(p["status"] in OPEN_PREVIOUS and p.get("finding_id") not in ids
                                 for p in review.get("previous_findings", []))
    if not open_code:
        return set()
    return {f["id"] for f in own(review) if f.get("gate") == "code_settled"}


def in_classes(f):
    """An extend_scope finding asks for a fix in this change, so it sits with the change's findings until an issue
    takes it over."""
    if origin(f) == "preexisting":
        return f["disposition"] == "extend_scope" and not f.get("follow_up_url")
    return origin(f) == "change"


def id_key(f):
    """Order F2 before F10: the verifier numbers findings in severity order."""
    m = re.fullmatch(r"(\D*)(\d+)", f["id"])
    return (m.group(1), int(m.group(2))) if m else (f["id"], 0)


def by_impact(findings):
    return sorted(findings, key=lambda f: (SEVERITIES.index(f["severity"]), id_key(f)))


def highest(findings):
    return min(SEVERITIES.index(f["severity"]) for f in findings)


def render(review):
    target = review["target"]
    out = [f"# Review ledger: {target.get('title') or target['url']}", "",
           f"{target['url']} · revision {review['revision']['head']}", "", result_line(review)]
    axes = review.get("axes", [])
    groups = {s: [a for a in axes if a["status"] == s] for s in ("ran", "skipped", "failed")}

    def names(items):
        return ", ".join(a["axis"] + (f" ({a['reason']})" if a.get("reason") else "") for a in items) or "none"

    if axes:
        out.append(f"Axes run: {names(groups['ran'])}; "
                   f"skipped: {names(groups['skipped'])}; failed: {names(groups['failed'])}")
    if review.get("scope_exclusions"):
        out.append(f"Out of scope: {'; '.join(e.rstrip('.') for e in review['scope_exclusions'])}")
    out.append("")

    held_ids = held(review)
    shown = [f for f in review["findings"] if f["id"] not in held_ids and in_classes(f)]
    class_ids = {c["id"] for c in review.get("classes", [])}
    groups = []
    for c in review.get("classes", []):
        members = [f for f in shown if f.get("class") == c["id"]]
        if members:
            head = [f"## Class {c['id']}: {c['title']}", ""]
            if c.get("root_cause"):
                head += [f"Root cause: {c['root_cause']}", ""]
            groups.append((head, members))
    loose = [f for f in shown if f.get("class") not in class_ids]
    if loose:
        groups.append((["## Findings without a class", ""], loose))
    for head, members in sorted(groups, key=lambda g: highest(g[1])):
        out += head
        for f in by_impact(members):
            out += finding(f)
    if held_ids:
        out += ["## Held until the code is settled", ""]
        for f in by_impact([f for f in review["findings"] if f["id"] in held_ids]):
            out += finding(f)
    follow_ups = [f for f in review["findings"] if origin(f) == "preexisting" and not in_classes(f)]
    if follow_ups:
        out += ["## Older than this change", ""]
        for f in by_impact(follow_ups):
            out += finding(f)
    stack = [f for f in review["findings"] if origin(f) == "stack"]
    if stack:
        out += ["## Made by other requests", ""]
        for f in by_impact(stack):
            out += finding(f)
    if review.get("previous_findings"):
        out += ["## Previous findings", ""]
        for p in review["previous_findings"]:
            ref = f" (continued by {p['finding_id']})" if p.get("finding_id") else ""
            line = f"- {p['thread_url']}: {p['status']}{ref}; {p['reason']}"
            if p.get("reply_urls"):
                line += f" Replies: {', '.join(p['reply_urls'])}."
            if p.get("follow_up_url"):
                line += f" Follow-up: {p['follow_up_url']}."
            out.append(line)
        out.append("")
    if review.get("open_questions"):
        out += ["## Needed to complete the review", ""]
        out += [f"- {q}" for q in review["open_questions"]]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    if len(sys.argv) not in (2, 3):
        fail("usage: render-ledger.py <review.json> [<ledger.md>]")
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) == 3 else os.path.join(os.path.dirname(os.path.abspath(src)), "ledger.md")
    with open(src, encoding="utf-8") as fh:
        review = json.load(fh)
    check(review)
    try:
        text = render(review)
    except KeyError as e:
        fail(f"missing field {e}")
    with open(dst, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(dst)


if __name__ == "__main__":
    main()
