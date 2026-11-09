# Regression cases for adr-authoring

Each directory here is one case: a frozen input in `prompt.md`, the checks in its `README.md`, and the results of each
model under `<model>/`. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is
re-run and how its results are committed.

## Running a case

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/<case> opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/<case>
```

The script copies the skill and `english-developer-style` out of the checkout, runs `claude -p` in safe mode in a
temporary directory with the Read tool alone, and writes `<model>/<name>.md`, `<model>/<name>.run.txt`, and
`<model>/skill-tree`. `--baseline` runs the same prompt with `english-developer-style` alone and writes under
`<model>/baseline/`. A PASS from `check.py` is a marker found, not a grade: read each result against the case README.

Each case carries its noise input in the same prompt, as a second change or a second request, so that one run shows
both the rule firing and the rule staying quiet.

A grade records what the result means. Where a result names a verdict in words of its own, such as "violated" or "not
met", the check fails on the marker and the README says whether the meaning matches; the checker cases test the five
verdicts of the skill, so a synonym still fails them. Where a result keeps a value open with "TBD" instead of a
placeholder in angle brackets, the README grades the meaning too.

Not covered yet: a request that states a decision is accepted with nothing open, which should give `Accepted`; a
repository whose records use another template; and a review with a reading guide that maps the layers.

## The cases

| Case | Side | Rules |
| --- | --- | --- |
| [`checker-partial-delivery`](checker-partial-delivery/README.md) | checker | `Implements` claims every case; a deferral leaves only the altered cases judged |
| [`checker-open-point`](checker-open-point/README.md) | checker | a check deleted under an open point is `Violates`; an allowance the open point decides is `Cannot tell` |
| [`checker-proposed-replacement`](checker-proposed-replacement/README.md) | checker | a `Proposed` replacement binds nothing until accepted; an untouched deferred rule is `Deferred` |
| [`writer-vague-notes`](writer-vague-notes/README.md) | writer | a placeholder and an open point for a value the notes leave open; the first record adds the guide |
| [`writer-accepted-record`](writer-accepted-record/README.md) | writer | an added requirement goes into a new record; a broken link is fixed in place |
| [`writer-two-decisions`](writer-two-decisions/README.md) | writer | two decisions get a proposed split; one decision stays one record |
