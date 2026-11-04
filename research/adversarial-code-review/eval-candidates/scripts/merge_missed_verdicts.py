#!/usr/bin/env python3
"""Join missed-defect candidates with the judge's verdicts, one line per culprit.

The candidates come from find_missed_defects.py, one per (blamer, culprit) pair;
the verdicts from prompts/prompt-judge-missed-defects.md, one per candidate, in
the same order. Pairs judged "unrelated" are dropped, and the text around each
reference stays in the candidates file: it is other people's text, and the
judge's one-sentence defect replaces it. A culprit's verdict is "introduced"
when any blamer's is, and "likely" otherwise; it is reviewable when any blamer
judged it so. The blamers are kept in the order they were filed. A line of
--overrides with repo, culprit, and verdict replaces the culprit's verdict and
adds the reason; data/overrides.jsonl uses "flagged-in-review" for a defect a
reviewer pointed out before the merge.

Usage: merge_missed_verdicts.py --pair pgjdbc.jsonl pgjdbc.verdicts.jsonl \
         --pair NullAway.jsonl NullAway.verdicts.jsonl --out data/missed-defects.jsonl \
         [--overrides data/overrides.jsonl]
"""
from __future__ import annotations

import argparse
import collections
import json

VERDICT_FIELDS = ("verdict", "defect_kind", "reviewable", "defect")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pair", nargs=2, action="append", required=True, metavar=("CANDIDATES", "VERDICTS"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--overrides", help="JSON Lines of corrections; a line with repo, culprit, and verdict replaces a verdict")
    args = ap.parse_args()

    kept = []
    for cand_path, verdict_path in args.pair:
        cands = [json.loads(line) for line in open(cand_path) if line.strip()]
        verdicts = [json.loads(line) for line in open(verdict_path) if line.strip()]
        if len(cands) != len(verdicts):
            raise SystemExit(f"{verdict_path} has {len(verdicts)} verdicts for {len(cands)} candidates in {cand_path}")
        for c, v in zip(cands, verdicts):
            if (c["blamer"], c["culprit"]) != (v["blamer"], v["culprit"]):
                raise SystemExit(f"{verdict_path}: verdict for #{v['blamer']} -> #{v['culprit']} is on the line of "
                                 f"#{c['blamer']} -> #{c['culprit']}")
            if v["verdict"] != "unrelated":
                kept.append(dict(c, **{k: v[k] for k in VERDICT_FIELDS}))

    overrides = {}
    if args.overrides:
        overrides = {(o["repo"], o["culprit"]): o for o in map(json.loads, open(args.overrides)) if "culprit" in o}

    by_culprit = collections.defaultdict(list)
    for r in kept:
        by_culprit[(r["repo"], r["culprit"])].append(r)
    unknown = set(overrides) - set(by_culprit)
    if unknown:
        raise SystemExit(f"{args.overrides} names culprits with no candidate: {', '.join(f'{r}#{n}' for r, n in unknown)}")
    with open(args.out, "w") as out:
        for (repo, culprit), rows in sorted(by_culprit.items()):
            rows.sort(key=lambda r: r["blamer_created"])
            override = overrides.get((repo, culprit))
            verdict = "introduced" if any(r["verdict"] == "introduced" for r in rows) else "likely"
            extra = dict(verdict_override=override["reason"]) if override else {}
            out.write(json.dumps(dict(
                repo=repo, culprit=culprit, culprit_title=rows[0]["culprit_title"],
                culprit_merged=rows[0]["culprit_merged"],
                verdict=override["verdict"] if override else verdict, **extra,
                reviewable=any(r["reviewable"] for r in rows),
                blamers=[dict(number=r["blamer"], kind=r["blamer_kind"], title=r["blamer_title"],
                              created=r["blamer_created"], fix_prs=r["fix_prs"], verdict=r["verdict"],
                              defect_kind=r["defect_kind"], defect=r["defect"])
                         for r in rows],
            )) + "\n")
    print(f"{len(by_culprit)} culprit pull requests written to {args.out}")


if __name__ == "__main__":
    main()
