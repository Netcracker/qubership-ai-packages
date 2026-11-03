# Regression cases for telemetry-authoring

Each directory here is one case: a frozen input in `prompt.md`, the checks in its `README.md`, and the results of each
model under `<model>/`. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is
re-run and how its results are committed. The inputs are written for the case; the two with a real counterpart restate
the facts of the earlier trials (`../ab-max-result-buffer.md`, `../ab-verify-release-deps.md`) as notes, so a run needs
no checkout.

## Running a case

From the repository root:

```bash
research/telemetry-authoring/cases/run-case.sh research/telemetry-authoring/cases/<case> opus result
```

The script copies telemetry-authoring and the American english-developer-style out of the checkout, runs `claude -p` in
safe mode in a temporary directory with the Read tool alone, and writes `<model>/<name>.md`, `<model>/<name>.run.txt`
(cost, tokens, turns), and `<model>/skill-tree`. A fourth argument takes telemetry-authoring from a commit and writes
under `<model>/baseline/`; the committed baselines ran on `9d2eab7`, the skill before the conditions these cases test.
english-developer-style comes from the working copy in both arms, because the skill hands it the wording.

Then grade the results:

```bash
python3 research/telemetry-authoring/cases/check.py research/telemetry-authoring/cases/<case>
```

`check.py` prints PASS, FAIL, or READ for every check of every result. A PASS means the marker was found, not that the
check passed: read the result against the check's question in the case README before recording a grade.

## The cases

| Case | Input | Rules |
| --- | --- | --- |
| [`error-negative-timeout`](error-negative-timeout/README.md) | a library rejecting a negative argument | negative control: the message names the value and the parameter and stops |
| [`cli-rejects-argument`](cli-rejects-argument/README.md) | a CLI rejecting its flag | negative control, outside the JVM |
| [`limit-max-result-buffer`](limit-max-result-buffer/README.md) | a limit set in a connection property | why, where to change it, and a way out other than raising it |
| [`build-check-release-jars`](build-check-release-jars/README.md) | a build check against a committed list | why, the diagnose command, each way out, what to report |
| [`review-retry-loop`](review-retry-loop/README.md) | a review of a retry loop | the findings, without a padded checklist, a stack line, or an instrument for a covered fact |

## Not covered

The conditions 1.2.0 added are exercised on the side where they keep an item out. The side where each lets the item
back in has no case yet: a stack line proposed where the imports and the build leave the logging API ambiguous; a review
note where a reviewer would expect a branch to emit; a limit on a request whose size the caller does not choose, where
the change to the request stays out of the message; an instrument a semantic convention defines; and a state whose
counterpart is the error returned to the caller. No case reaches the deleted rule that counted every recurring logged
condition (see `review-retry-loop`).
