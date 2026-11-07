"""Scores every classifier in classifiers.json against the ground truth and rewrites results.md and dataset.md.

Run it after adding a classifier's predictions as preds/<id>.jsonl and its entry in classifiers.json:
    python3 scripts/report.py
Standard library only; deterministic (the bootstrap is seeded).
"""
import json
import os
import random
import sys
import zlib
from bisect import bisect_left, bisect_right

from common import AXES, load_preds, path, prs

GT_DIR, RERUN_DIR = "claude-opus-5-5", "claude-opus-5-5-rerun"
BOOT = 1000
DOCS_CASE = "apache_calcite_5278"      # the JDK bump whose docs update was missed in review


def load(d):
    return {os.path.basename(f)[:-5]: json.load(open(os.path.join(d, f))) for f in os.listdir(d) if f.endswith(".json")}


GT = load(path("labels", GT_DIR))
K = [p["key"] for p in prs() if p["key"] in GT]


def required(k, a, gt=GT):
    return gt[k]["axes"][a]["label"] == 2


def p_required(pred, a):
    """Probability-like score that the axis is required: P(2) for System One answers, p_required for LLMs."""
    x = pred["axes"][a]
    if "p" in x:
        return float(x["p"]["2"])
    return float(x.get("p_required", x["label"] / 2))


def own_label(pred, a):
    """The classifier's own call: expected score >= 1 (P >= 0.5 for yes/no) for System One answers, the label for LLMs."""
    x = pred["axes"][a]
    if "p" in x:
        return 2 if x["score"] >= 1.0 else (0 if x["score"] < 0.5 else 1)
    return int(x["label"])


def own_split(pred):
    if "plan_split" in pred:
        return pred["plan_split"] >= 0.5
    return (pred.get("plan") or {}).get("mode") == "split"


def auc(pairs):
    """Mann-Whitney AUC of (score, is_positive) pairs, ties counted as half."""
    neg = sorted(s for s, y in pairs if not y)
    pos = [s for s, y in pairs if y]
    if not pos or not neg:
        return float("nan")
    return sum(bisect_left(neg, s) + 0.5 * (bisect_right(neg, s) - bisect_left(neg, s)) for s in pos) / (len(pos) * len(neg))


def r_precision(pairs):
    n = sum(y for _, y in pairs)
    return sum(y for _, y in sorted(pairs, key=lambda p: -p[0])[:n]) / n


def by_pr(pred, ks):
    return {k: [(p_required(pred[k], a), required(k, a)) for a in AXES] for k in ks}


def boot_ci(per_pr, f, seed):
    rnd = random.Random(seed)
    ks = list(per_pr)
    vals = sorted(f([x for _ in ks for x in per_pr[rnd.choice(ks)]]) for _ in range(BOOT))
    return vals[int(0.025 * BOOT)], vals[int(0.975 * BOOT)]


def counts_at(pairs, t):
    tp = sum(1 for s, y in pairs if y and s >= t)
    fp = sum(1 for s, y in pairs if not y and s >= t)
    return tp, fp, sum(y for _, y in pairs) - tp


def repo_of(key):
    return key.rsplit("_", 1)[0]


def loro(per_pr):
    """Threshold picked for the best F1 on two repositories, applied to the third; held-out counts pooled.
    Returns precision, recall, flagged axes per PR, and the held-out threshold of each repository."""
    repos = sorted({repo_of(k) for k in per_pr})
    tp = fp = fn = 0
    thresholds = {}
    for held in repos:
        train = [x for k, v in per_pr.items() if not k.startswith(held) for x in v]
        test = [x for k, v in per_pr.items() if k.startswith(held) for x in v]
        best = max(((2 * c[0] / (2 * c[0] + c[1] + c[2]) if c[0] else 0), t / 100)
                   for t in range(1, 100) for c in [counts_at(train, t / 100)])
        a, b, c = counts_at(test, best[1])
        tp, fp, fn = tp + a, fp + b, fn + c
        thresholds[held] = best[1]
    return tp / max(tp + fp, 1), tp / max(tp + fn, 1), (tp + fp) / len(per_pr), thresholds


def fmt(x, d=2):
    return "n/a" if x != x else f"{x:.{d}f}"


def main():
    reg = json.load(open(path("classifiers.json")))
    rows = []
    for c in reg:
        f = path("preds", f"{c['id']}.jsonl")
        if not os.path.exists(f):
            print(f"classifiers.json lists {c['id']}, but {f} does not exist; skipped", file=sys.stderr)
            continue
        pred = load_preds(c["id"])
        ks = [k for k in K if k in pred]
        per = by_pr(pred, ks)
        flat = [x for v in per.values() for x in v]
        lo, hi = boot_ci(per, auc, zlib.crc32(c["id"].encode()))   # seeded by id: a new entry moves no other row
        p, r, flagged, thr = loro(per)
        own = [(own_label(pred[k], a) == 2, required(k, a)) for k in ks for a in AXES]
        tp = sum(1 for o, y in own if o and y)
        split_gt = [k for k in ks if GT[k]["plan"]["mode"] == "split"]
        mand = [(p_required(pred[k], a) >= thr[repo_of(k)]) for k in ks for a in AXES if required(k, a) and GT[k]["axes"][a]["mandated"]]
        find = [(p_required(pred[k], a) >= thr[repo_of(k)]) for k in ks for a in AXES if required(k, a) and not GT[k]["axes"][a]["mandated"]]
        rows.append(dict(c, n=len(ks), auc=auc(flat), lo=lo, hi=hi, rprec=r_precision(flat), loro_p=p, loro_r=r,
                         flagged=flagged,
                         own_p=tp / max(sum(o for o, _ in own), 1), own_r=tp / max(sum(y for _, y in own), 1),
                         plan_acc=sum(own_split(pred[k]) == (GT[k]["plan"]["mode"] == "split") for k in ks) / len(ks),
                         split_rec=f"{sum(own_split(pred[k]) for k in split_gt)}/{len(split_gt)}",
                         cost=sum(pred[k].get("cost_usd", 0) for k in ks) / len(ks),
                         latency=sum(pred[k].get("latency_s", 0) for k in ks) / len(ks),
                         axis_auc={a: auc([(p_required(pred[k], a), required(k, a)) for k in ks]) for a in AXES},
                         mand=sum(mand) / max(len(mand), 1), find=sum(find) / max(len(find), 1), n_mand=len(mand), n_find=len(find),
                         docs_case=p_required(pred[DOCS_CASE], "user_docs") if DOCS_CASE in pred else float("nan")))
    write_results(rows)
    write_dataset()


def write_results(rows):
    n_req = sum(required(k, a) for k in K for a in AXES)
    L = ["# Results", "",
         "Generated by `scripts/report.py`; do not edit by hand. The method, the caveats, and how to add a classifier are in",
         "[README.md](README.md).", "",
         f"Ground truth: `labels/{GT_DIR}`, {len(K)} PRs, {n_req} required axis-PR pairs of {len(K) * len(AXES)} "
         f"({n_req / len(K):.1f} per PR), {sum(GT[k]['plan']['mode'] == 'split' for k in K)} PRs to split.", "",
         "## Quality and cost", "",
         "- AUC: ranking of all PR x axis pairs by the classifier's P(required); 95% CI from a bootstrap over PRs.",
         "- R-prec: precision among the top N pairs, N = number of required pairs.",
         "- LORO P/R/axes: threshold tuned on two repositories and applied to the third; axes = axes flagged per PR.",
         "- Own P/R: the classifier's own labels (System One: expected score >= 1).",
         "- Split acc/recall: the classifier's own single-vs-split call against the labeler's.",
         "- $/PR at list price; latency is wall time per PR as measured (Jev with 4 requests in flight).", "",
         "| Classifier | Model | Input | AUC [95% CI] | R-prec | LORO P | LORO R | LORO axes/PR | Own P | Own R | Split acc | Split recall | $/PR | s/PR |",
         "|" + " --- |" * 14]
    for r in rows:
        L.append(f"| `{r['id']}` | {r['model']} | {r['input']} | {fmt(r['auc'])} [{fmt(r['lo'])}-{fmt(r['hi'])}] | {fmt(r['rprec'])} | "
                 f"{fmt(r['loro_p'])} | {fmt(r['loro_r'])} | {r['flagged']:.1f} | {fmt(r['own_p'])} | {fmt(r['own_r'])} | "
                 f"{fmt(r['plan_acc'])} | {r['split_rec']} | {r['cost']:.4f} | {r['latency']:.1f} |")
    L += ["", "## AUC per axis", "", "| Axis | Required | " + " | ".join(f"`{r['id']}`" for r in rows) + " |",
          "|" + " --- |" * (len(rows) + 2)]
    for a in AXES:
        L.append(f"| {a} | {sum(required(k, a) for k in K)} | " + " | ".join(fmt(r["axis_auc"][a]) for r in rows) + " |")
    L += ["", "## Recall by why the axis was required", "",
          "Each PR at the threshold tuned on the other two repositories. Mandated: the kind of change requires the check. Finding only: the labeler",
          "found a defect or omission on an axis the change type does not mandate.", "",
          "| Classifier | Mandated recall | Finding-only recall |", "| --- | --- | --- |"]
    for r in rows:
        L.append(f"| `{r['id']}` | {fmt(r['mand'])} (n={r['n_mand']}) | {fmt(r['find'])} (n={r['n_find']}) |")
    L += ["", f"## The docs case: `{DOCS_CASE}` user_docs", "",
          "The JDK bump whose documentation update was missed in review (ground truth: required).", "",
          "| Classifier | P(required) |", "| --- | --- |"]
    L += [f"| `{r['id']}` | {fmt(r['docs_case'])} |" for r in rows]
    L += ["", "## Single versus split: size rules", "", "| Rule | Accuracy | Split recall | False splits |", "| --- | --- | --- | --- |"]
    lines = {p["key"]: p["changed_lines"] for p in prs()}
    gt = {k: GT[k]["plan"]["mode"] == "split" for k in K}
    for n in (300, 500, 800, 1200):
        pred = {k: lines[k] > n for k in K}
        L.append(f"| changed lines > {n} | {sum(pred[k] == gt[k] for k in K) / len(K):.2f} | "
                 f"{sum(pred[k] and gt[k] for k in K)}/{sum(gt.values())} | {sum(pred[k] and not gt[k] for k in K)} |")
    rerun = load(path("labels", RERUN_DIR))
    both = [k for k in K if k in rerun]
    if both:
        a1 = [required(k, a) for k in both for a in AXES]
        a2 = [required(k, a, rerun) for k in both for a in AXES]
        n = len(a1)
        po = sum(x == y for x, y in zip(a1, a2)) / n
        pa, pb = sum(a1) / n, sum(a2) / n
        pe = pa * pb + (1 - pa) * (1 - pb)
        L += ["", "## Labeler agreement", "",
              f"`labels/{GT_DIR}` against an independent rerun `labels/{RERUN_DIR}` on {len(both)} PRs: "
              f"Cohen's kappa on required = {(po - pe) / (1 - pe):.2f}; required pairs {sum(a1)} and {sum(a2)}, "
              f"{sum(x and y for x, y in zip(a1, a2))} in common; review plan matches on "
              f"{sum(GT[k]['plan']['mode'] == rerun[k]['plan']['mode'] for k in both)} of {len(both)}."]
    open(path("results.md"), "w").write("\n".join(L) + "\n")


def write_dataset():
    L = ["# Dataset", "",
         "Generated by `scripts/report.py` from `dataset/prs.json` and the ground truth. Size: S < 40 changed lines,",
         "M < 400, L otherwise, counted on the initial version.", "",
         "| PR | Title | Size | What it does | Required axes (ground truth) | Plan |", "| --- | --- | --- | --- | --- | --- |"]
    for p in prs():
        g = GT[p["key"]]
        req = ", ".join(a for a in AXES if g["axes"][a]["label"] == 2) or "none"
        title = p["title"].replace("|", "\\|").replace("[", "\\[").replace("]", "\\]")
        summary = g["summary"].replace("|", "\\|")
        L.append(f"| [{p['repo']}#{p['number']}]({p['url']}) | {title} | {p['size']} | {summary} | {req} | {g['plan']['mode']} |")
    open(path("dataset.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
