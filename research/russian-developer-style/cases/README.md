# Regression cases for russian-developer-style

Each directory here is one case: a frozen input in `prompt.md`, the checks in its `README.md`, and the results of each
model under `<model>/`. `agent-packages/AGENTS.md`, section "Testing a skill against its cases", says when a case is
re-run and how its results are committed. The inputs are written for the case, not copied from a real project.

## Running a case

From the repository root:

```bash
research/russian-developer-style/cases/run-case.sh research/russian-developer-style/cases/<case> opus result
```

The script copies the skill out of the checkout, runs `claude -p` in safe mode in a temporary directory with the Read
tool alone, and writes `<model>/<name>.md`, `<model>/<name>.run.txt` (cost, tokens, turns), and `<model>/skill-tree`. A
fourth argument takes the skill from a commit and writes under `<model>/baseline/`; the committed baselines ran on
`51b8d41`, the skill before the rules these cases test.

Then grade the results:

```bash
python3 research/russian-developer-style/cases/check.py research/russian-developer-style/cases/<case>
```

`check.py` prints PASS or FAIL for every check of every result. The verdict is the script's reading of a marker, found
or absent, not a grade: read the result against the check's question in the case README before recording one.

`python3 -m doctest research/russian-developer-style/cases/check.py` runs the examples in the checks' docstrings.

## The cases

Each negative control sits beside a case where the same item still belongs.

| Case | Input | Rules |
| --- | --- | --- |
| [`error-negative-fetch-size`](error-negative-fetch-size/README.md) | a trivial validation | negative control: no action and no «Не удалось» where the fix is undoing the value |
| [`error-config-unreadable`](error-config-unreadable/README.md) | a config file the user cannot read | an action where the fix is not undoing the value |
| [`commit-typo`](commit-typo/README.md) | a one-line typo fix | negative control: the subject is the whole message |
| [`commit-stale-token`](commit-stale-token/README.md) | a non-obvious retry fix | a body that says why |
| [`docstring-len`](docstring-len/README.md) | `Len() int` | negative control: one sentence, no parameter or result section |
| [`docstring-parse-port`](docstring-parse-port/README.md) | a parser with two errors | the errors and the range are documented |
| [`pr-dependency-bump`](pr-dependency-bump/README.md) | a one-line dependency bump | negative control: no «Как проверить», no risks, at most 40 words |
| [`empty-mentions`](empty-mentions/README.md) | an empty list the user cannot fill | negative control: no action to create |
| [`empty-alert-rules`](empty-alert-rules/README.md) | an empty list the user can fill | an action to create |

`pr-dependency-bump` has no presence pair: which parts a larger description carries is `change-description-authoring`'s,
and its cases cover them.
