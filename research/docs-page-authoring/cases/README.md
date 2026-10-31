# Regression cases for docs-page-authoring

Each directory here is one case: a frozen input in `prompt.md`, the checks in its `README.md`, and the results of each
model under `<model>/`. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is
re-run and how its results are committed. Both cases share the reference page in `page.md`, an options page of a
made-up HTTP client, so that no model recalls the real entry.

## Running a case

From the repository root:

```bash
research/docs-page-authoring/cases/run-case.sh research/docs-page-authoring/cases/<case> opus result
```

The script copies docs-page-authoring and the American english-developer-style out of the checkout, runs `claude -p`
in safe mode in a temporary directory with the Read tool alone, and writes `<model>/<name>.md`, `<model>/<name>.run.txt`
(cost, tokens, turns), and `<model>/skill-tree`. A fourth argument takes docs-page-authoring from a commit and writes
under `<model>/baseline/`; english-developer-style always comes from the working copy. The committed baselines ran on
`51b8d41`, where docs-page-authoring is the same as at `9d2eab7`: every slot of an option entry, regardless.

Then count the markers:

```bash
python3 research/docs-page-authoring/cases/check.py research/docs-page-authoring/cases/<case>
```

A PASS means the marker was found, not that the check passed: read the result against the check's question in the case
README before recording a grade.

## The cases

| Case | Input | Rules |
| --- | --- | --- |
| [`boolean-option`](boolean-option/README.md) | a new boolean with no limit, no interaction, on a page with no version markers | negative control: the header and the claim, and no other slot |
| [`limit-option`](limit-option/README.md) | a new size limit with an error, a mode that turns its default off, and a reason to raise it | every slot that has content stays |
