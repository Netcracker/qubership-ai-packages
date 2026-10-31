# Regression cases for english-developer-style

Each directory here is one case: a frozen input in `prompt.md`, the checks in its `README.md`, and the results of each
model under `<model>/`. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is
re-run and how its results are committed. The inputs are written for the case, not copied from a real thread.

## Running a case

From the repository root:

```bash
research/english-developer-style/cases/run-case.sh research/english-developer-style/cases/<case> opus result
```

The script copies the American skill out of the checkout, runs `claude -p` in safe mode in a temporary directory with
the Read tool alone, and writes `<model>/<name>.md`, `<model>/<name>.run.txt` (cost, tokens, turns), and
`<model>/skill-tree`. A fourth argument takes the skill from a commit and writes under `<model>/baseline/`; the
committed baselines ran on `9d2eab7`, the skill before the rules these cases test. The British skill differs from the
American one in spelling and quotation style only, so the cases run the American one.

Then grade the results:

```bash
python3 research/english-developer-style/cases/check.py research/english-developer-style/cases/<case>
```

`check.py` prints PASS, FAIL, or READ for every check of every result. A PASS means the marker was found, not that the
check passed: read the result against the check's question in the case README before recording a grade.

## The cases

| Case | Input | Rules |
| --- | --- | --- |
| [`review-nit-fixed`](review-nit-fixed/README.md) | a one-line nit, fixed | negative control: no section, heading, or restatement for one point |
| [`review-three-points`](review-three-points/README.md) | a review comment with three points | a section per point, opened by an exact quote; what holds before the dispute |
| [`error-negative-fetch-size`](error-negative-fetch-size/README.md) | a trivial validation | negative control: no action and no consequence where the fix is undoing the input |
| [`error-config-unreadable`](error-config-unreadable/README.md) | a config file the user cannot read | an action where the fix is not undoing the input; no consequence where execution stops |
