#!/usr/bin/env python3
"""Build the generated parts of a review dossier from findings.jsonl.

Usage:
    findings-csv.py <dossier>               write findings.csv and fill the generated blocks
    findings-csv.py <dossier> --import-csv  copy verdict and rejection_reason from findings.csv back into findings.jsonl

Decisions may be entered in either file. work/findings-csv.base.json records the decisions as the last build wrote
them into findings.csv, so a later run can tell which side changed: a change made only in findings.csv is imported
with --import-csv, a change made only in findings.jsonl is written into the next findings.csv, and a finding changed
differently in both is reported and left for a person to settle.

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
DECISION_KEYS = ("verdict", "rejection_reason")
BASE = Path("work") / "findings-csv.base.json"
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


def output_path(dossier, relative):
    """The path of a file this script writes, refused when it would land outside the dossier.

    The dossier lives inside the reviewed repository and agents write into it, so any file in it may be a symbolic
    link by the time this script runs.
    """
    path = dossier / relative
    if path.is_symlink() or not path.resolve().is_relative_to(dossier):
        raise SystemExit(f"{path}: is a symbolic link or resolves outside {dossier}; refusing to write it")
    return path


def decision(record):
    return tuple((record.get(k) or "").strip() for k in DECISION_KEYS)


def load_base(dossier):
    path = dossier / BASE
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as fh:
        return {fid: tuple(value) for fid, value in json.load(fh).items()}


def write_base(dossier, findings):
    path = output_path(dossier, BASE)
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({f["id"]: decision(f) for f in findings}, fh, ensure_ascii=False, indent=0)
        fh.write("\n")


def compare_decisions(dossier, findings):
    """Split the findings whose decision differs between findings.csv and findings.jsonl by the side that changed.

    Returns (from_csv, conflicts): `from_csv` maps an id to the CSV row whose decision changed only in the CSV;
    `conflicts` lists (id, csv decision, jsonl decision) where both changed, where no base records what the CSV was
    written with, or where the id is on no line of findings.jsonl any more. A decision changed only in findings.jsonl
    is in neither: the next build writes it into the CSV.

    A row whose id a re-run of the consolidator merged into another line is compared with that line, found through
    its `sources`.
    """
    path = dossier / "findings.csv"
    if not path.exists():
        return {}, []
    current = lines_by_id(findings)
    base = load_base(dossier)
    from_csv, conflicts = {}, []
    for row in read_csv(path):
        fid = row["id"]
        if fid not in current:
            if any(decision(row)):
                conflicts.append((fid, decision(row), None))
            continue
        in_csv, in_jsonl = decision(row), decision(current[fid])
        if in_csv == in_jsonl:
            continue
        written = base.get(fid) if base is not None else None
        if written is not None and in_csv == written:
            continue
        if written is not None and in_jsonl == written:
            from_csv[fid] = row
        else:
            conflicts.append((fid, in_csv, in_jsonl))
    return from_csv, conflicts


def lines_by_id(findings):
    """Map every id to the line of findings.jsonl that carries it, as its own id or as one of its sources."""
    lines = {}
    for f in findings:
        for _, source_id in sources(f):
            lines.setdefault(source_id, f)
    lines.update({f["id"]: f for f in findings})
    return lines


def report_conflicts(conflicts, base_missing):
    reason = (
        "work/findings-csv.base.json is missing, so it is unknown which file is newer"
        if base_missing
        else "both files changed since findings.csv was written"
    )
    print(f"findings.csv and findings.jsonl disagree, and {reason}:", file=sys.stderr)
    for fid, in_csv, in_jsonl in conflicts:
        jsonl = "has no line with this id" if in_jsonl is None else repr(in_jsonl)
        print(f"  {fid}: findings.csv {in_csv!r}, findings.jsonl {jsonl}", file=sys.stderr)
    print("Set the decision you want in both files, then run the script again.", file=sys.stderr)


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
    with open(output_path(dossier, "findings.csv"), "w", encoding="utf-8", newline="") as fh:
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
    write_base(dossier, findings)


def replace_block(dossier, relative, name, body, problems):
    path = output_path(dossier, relative)
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
    from_csv, conflicts = compare_decisions(dossier, findings)
    if conflicts:
        report_conflicts(conflicts, load_base(dossier) is None)
        return 1
    if from_csv:
        ids = sorted(from_csv)
        print(
            f"findings.csv holds decisions findings.jsonl lacks ({', '.join(ids[:5])}{', …' if len(ids) > 5 else ''});"
            " run with --import-csv first",
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
        replace_block(dossier, path.relative_to(dossier), "evidence", evidence_block(members, mention_map), problems)

    readme = dossier / "README.md"
    if readme.exists():
        titles = {slug: issue_title(p) for slug, p in issue_files.items()}
        replace_block(dossier, "README.md", "standalone", standalone_block(findings, mention_map), problems)
        components = {slug: issue_component(p) for slug, p in issue_files.items()}
        replace_block(dossier, "README.md", "components", components_block(findings, titles, components), problems)
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
    findings = load_findings(dossier)
    decisions, conflicts = compare_decisions(dossier, findings)
    if conflicts:
        report_conflicts(conflicts, load_base(dossier) is None)
        print("findings.jsonl left unchanged.", file=sys.stderr)
        return 1
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
    lines = lines_by_id(findings)
    targets = {}
    for fid, row in decisions.items():
        targets.setdefault(id(lines[fid]), []).append((fid, decision(row)))
    split = [ids for ids in targets.values() if len({d for _, d in ids}) > 1]
    if split:
        print("findings.jsonl left unchanged: rows merged into one finding carry different decisions:", file=sys.stderr)
        for ids in split:
            print("  " + ", ".join(f"{fid} {d!r}" for fid, d in ids), file=sys.stderr)
        return 1
    changed = 0
    for fid, row in decisions.items():
        f = lines[fid]
        for key in DECISION_KEYS:
            if (row.get(key) or "") != (f.get(key) or ""):
                f[key] = row.get(key) or ""
                changed += 1
    with open(output_path(dossier, "findings.jsonl"), "w", encoding="utf-8") as fh:
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
