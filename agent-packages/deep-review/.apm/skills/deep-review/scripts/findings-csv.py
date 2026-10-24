#!/usr/bin/env python3
"""Build the generated parts of a review dossier from findings.jsonl.

Usage:
    findings-csv.py <dossier>               write findings.csv and fill the generated blocks
    findings-csv.py <dossier> --import-csv  copy verdict and rejection_reason from findings.csv back into findings.jsonl

The consolidator writes the prose (README.md, issues/*.md); this script writes everything that is a lookup:
the CSV for the team's triage, and the blocks between `<!-- BEGIN generated:<name> -->` and
`<!-- END generated:<name> -->` markers:

    issues/<slug>.md  generated:evidence    the findings of that issue, with links to the axis reports
    README.md         generated:standalone  findings that belong to no issue, priority now or plan
    README.md         generated:components  issues and standalone findings per component

The script is idempotent: a second run replaces the blocks it wrote the first time.
"""

import csv
import json
import re
import sys
from pathlib import Path

PRIORITY_LABEL = {"now": "Чинить первым", "plan": "Запланировать", "later": "На усмотрение"}
PRIORITY_ORDER = {"now": 0, "plan": 1, "later": 2}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "ACCEPTED-DEBT": 4}
CONFIDENCE_LABEL = {"CONFIRMED": "воспроизведено", "PLAUSIBLE": "по коду"}
ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+\b")
VERDICTS = {"fix", "backlog", "reject"}
REJECTION_REASONS = {"convention", "guard-missed", "out-of-scope", "model-error", "accepted-debt"}
CSV_COLUMNS = [
    "id", "issue", "priority", "severity", "confidence", "component", "effort", "title", "file",
    "axes", "details", "mentioned_in", "verify_verdict", "verdict", "rejection_reason",
]


def anchor(finding_id):
    return finding_id.lower()


def sources(f):
    if f.get("sources"):
        return [(s["axis"], s["id"]) for s in f["sources"]]
    # Dossiers written before `sources` existed list the axes in the order of [id] + merged_from.
    ids = [f["id"]] + list(f.get("merged_from") or [])
    return [(axis, fid) for fid, axis in zip(ids, f.get("axes") or [])]


def is_refuted(f):
    return f.get("verify_verdict") == "refuted" or f.get("confidence") == "REFUTED"


def confidence_label(f):
    if is_refuted(f):
        return "снято при проверке"
    return CONFIDENCE_LABEL.get(f.get("confidence") or "", f.get("confidence") or "")


def load_findings(dossier):
    with open(dossier / "findings.jsonl", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def read_csv(path):
    """Read findings.csv as saved by the script or re-saved by a spreadsheet (BOM, `;` delimiter)."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        text = fh.read()
    dialect = csv.Sniffer().sniff(text.split("\n", 1)[0], delimiters=",;\t")
    rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    if rows and "id" not in rows[0]:
        raise SystemExit(f"{path}: no 'id' column; columns are {list(rows[0])}")
    return rows


def unimported_decisions(dossier, findings):
    """Ids whose verdict or rejection_reason in findings.csv differs from findings.jsonl."""
    path = dossier / "findings.csv"
    if not path.exists():
        return []
    current = {f["id"]: f for f in findings}
    return [
        row["id"] for row in read_csv(path)
        if row["id"] in current
        and any((row.get(k) or "") != (current[row["id"]].get(k) or "") for k in ("verdict", "rejection_reason"))
    ]


def anchors(dossier):
    """Map each axis to the lowercase anchor ids its report declares."""
    return {
        report.stem: set(re.findall(r'<a id="([^"]+)"', report.read_text(encoding="utf-8")))
        for report in (dossier / "reports").glob("*.md")
    }


def mentions(dossier):
    """Map each finding id to the axes whose report mentions it."""
    found = {}
    for report in sorted((dossier / "reports").glob("*.md")):
        for fid in set(ID_RE.findall(report.read_text(encoding="utf-8"))):
            found.setdefault(fid, set()).add(report.stem)
    return found


def mentioned_in(f, mention_map):
    own = {axis for axis, _ in sources(f)}
    ids = [fid for _, fid in sources(f)] or [f["id"]]
    return sorted({axis for fid in ids for axis in mention_map.get(fid, ())} - own)


def detail_links(f, prefix):
    return ", ".join(f"[{axis}]({prefix}reports/{axis}.md#{anchor(fid)})" for axis, fid in sources(f))


def report_links(axes, prefix):
    return ", ".join(f"[{axis}]({prefix}reports/{axis}.md)" for axis in axes) or "—"


def sort_key(f):
    return (
        PRIORITY_ORDER.get(f.get("priority") or "", 9),
        SEVERITY_ORDER.get(f.get("severity") or "", 9),
        0 if f.get("confidence") == "CONFIRMED" else 1,
        f["id"],
    )


def cell(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def write_csv(dossier, findings, mention_map):
    with open(dossier / "findings.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CSV_COLUMNS)
        for f in sorted(findings, key=sort_key):
            w.writerow([
                f["id"], f.get("issue") or "", f.get("priority") or "", f.get("severity") or "",
                confidence_label(f), f.get("component") or "", f.get("effort") or "", f.get("title") or "",
                f.get("file") or "", " ".join(a for a, _ in sources(f)),
                " ".join(f"reports/{a}.md#{anchor(i)}" for a, i in sources(f)),
                " ".join(mentioned_in(f, mention_map)), f.get("verify_verdict") or "",
                f.get("verdict") or "", f.get("rejection_reason") or "",
            ])


def replace_block(path, name, body, problems):
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(<!-- BEGIN generated:{name} -->\n).*?(<!-- END generated:{name} -->)", re.DOTALL
    )
    if not pattern.search(text):
        problems.append(f"{path.name}: no generated:{name} block")
        return
    path.write_text(pattern.sub(lambda m: m.group(1) + body + m.group(2), text, count=1), encoding="utf-8")


def evidence_block(issue_findings, mention_map):
    rows = [
        "| Находка | Серьёзность | Уверенность | Утверждение | Подробно в отчёте области | Также упоминают |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for f in sorted(issue_findings, key=sort_key):
        rows.append(
            f"| `{f['id']}` | {f.get('severity') or ''} | {confidence_label(f)} | {cell(f.get('title'))} "
            f"| {detail_links(f, '../')} | {report_links(mentioned_in(f, mention_map), '../')} |"
        )
    axes = sorted({a for f in issue_findings for a, _ in sources(f)})
    rows.append("")
    rows.append(f"Области проверки, которые подкрепляют проблему: {report_links(axes, '../')}.")
    return "\n".join(rows) + "\n"


def standalone_block(findings, mention_map):
    picked = [f for f in findings if not f.get("issue") and f.get("priority") in ("now", "plan") and not is_refuted(f)]
    if not picked:
        return "Все находки этих приоритетов входят в проблемы выше.\n"
    rows = [
        "| Находка | Приоритет | Утверждение | Где | Объём | Подробно |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for f in sorted(picked, key=sort_key):
        rows.append(
            f"| `{f['id']}` | {PRIORITY_LABEL[f['priority']]} | {cell(f.get('title'))} | `{cell(f.get('file'))}` "
            f"| {f.get('effort') or '—'} | {detail_links(f, '')} |"
        )
    return "\n".join(rows) + "\n"


def components_block(findings, issue_titles, issue_components):
    by_component = {}
    for f in findings:
        if is_refuted(f) or f.get("priority") not in ("now", "plan"):
            continue
        if f.get("issue"):
            number = f["issue"].split("-", 1)[0]
            label = f"карточка {number}" if number.isdigit() else issue_titles.get(f["issue"], f["issue"])
            entry = f"[{label}](issues/{f['issue']}.md)"
        else:
            axis, fid = (sources(f) or [(None, f["id"])])[0]
            entry = f"[`{f['id']}`](reports/{axis}.md#{anchor(fid)})" if axis else f"`{f['id']}`"
        # A card is listed once, under the component its header names; its findings may touch others.
        component = issue_components.get(f.get("issue")) or f.get("component") or "без компонента"
        by_component.setdefault(component, []).append((sort_key(f), entry))
    lines = []
    for component in sorted(by_component):
        entries = list(dict.fromkeys(entry for _, entry in sorted(by_component[component])))
        lines.append(f"- **{component}:** " + ", ".join(entries))
    return "\n".join(lines) + "\n"


def issue_component(path):
    match = re.search(r"\*\*Компонент:\*\*\s*([^·\n]+)", path.read_text(encoding="utf-8"))
    return match.group(1).strip() if match else None


def issue_title(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def build(dossier):
    findings = load_findings(dossier)
    pending = unimported_decisions(dossier, findings)
    if pending:
        print(
            f"findings.csv holds decisions findings.jsonl lacks ({', '.join(pending[:5])}"
            f"{', …' if len(pending) > 5 else ''}); run with --import-csv first, or delete findings.csv to discard them",
            file=sys.stderr,
        )
        return 1
    mention_map = mentions(dossier)
    write_csv(dossier, findings, mention_map)
    problems = []
    declared = anchors(dossier)
    for f in findings:
        for axis, fid in sources(f):
            if anchor(fid) not in declared.get(axis, set()):
                problems.append(f"{f['id']}: reports/{axis}.md has no <a id=\"{anchor(fid)}\"> anchor")

    issues_dir = dossier / "issues"
    issue_files = {p.stem: p for p in sorted(issues_dir.glob("*.md"))} if issues_dir.is_dir() else {}
    for slug in sorted({f["issue"] for f in findings if f.get("issue")} - issue_files.keys()):
        problems.append(f"findings point at issue {slug!r}, but issues/{slug}.md does not exist")
    for slug, path in issue_files.items():
        members = [f for f in findings if f.get("issue") == slug]
        if not members:
            problems.append(f"issues/{slug}.md: no finding has issue={slug!r}")
            continue
        replace_block(path, "evidence", evidence_block(members, mention_map), problems)

    readme = dossier / "README.md"
    if readme.exists():
        titles = {slug: issue_title(p) for slug, p in issue_files.items()}
        replace_block(readme, "standalone", standalone_block(findings, mention_map), problems)
        components = {slug: issue_component(p) for slug, p in issue_files.items()}
        replace_block(readme, "components", components_block(findings, titles, components), problems)
    else:
        problems.append("README.md does not exist")

    for f in findings:
        if not is_refuted(f) and f.get("priority") not in PRIORITY_ORDER:
            problems.append(f"{f['id']}: priority is {f.get('priority')!r}, expected now, plan, or later")
    print(f"findings.csv: {len(findings)} findings; {len(issue_files)} issue files")
    for p in problems:
        print(f"PROBLEM: {p}")
    return 1 if problems else 0


def import_csv(dossier):
    decisions = {row["id"]: row for row in read_csv(dossier / "findings.csv")}
    errors = []
    for fid, row in decisions.items():
        verdict, reason = (row.get("verdict") or "").strip(), (row.get("rejection_reason") or "").strip()
        if verdict and verdict not in VERDICTS:
            errors.append(f"{fid}: verdict {verdict!r}, expected one of {sorted(VERDICTS)}")
        if verdict == "reject" and reason not in REJECTION_REASONS:
            errors.append(f"{fid}: reject needs rejection_reason, one of {sorted(REJECTION_REASONS)}; got {reason!r}")
        if verdict != "reject" and reason:
            errors.append(f"{fid}: rejection_reason {reason!r} given without verdict reject")
        row["verdict"], row["rejection_reason"] = verdict, reason
    if errors:
        print("findings.jsonl left unchanged:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    findings = load_findings(dossier)
    changed = 0
    for f in findings:
        row = decisions.get(f["id"])
        if not row:
            continue
        for key in ("verdict", "rejection_reason"):
            if (row.get(key) or "") != (f.get(key) or ""):
                f[key] = row.get(key) or ""
                changed += 1
    with open(dossier / "findings.jsonl", "w", encoding="utf-8") as fh:
        for f in findings:
            fh.write(json.dumps(f, ensure_ascii=False) + "\n")
    print(f"findings.jsonl: {changed} fields updated from findings.csv")
    return 0


def main(argv):
    if len(argv) not in (2, 3) or (len(argv) == 3 and argv[2] != "--import-csv"):
        print(__doc__, file=sys.stderr)
        return 2
    dossier = Path(argv[1]).resolve()
    return import_csv(dossier) if len(argv) == 3 else build(dossier)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
