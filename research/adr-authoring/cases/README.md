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

The cases cover three kinds of decision of `agent-packages/adr-authoring/AGENTS.md`, all in one Go repository: the
behavior of a service, a structural invariant, and a cross-cutting requirement. The last is the platform the service
runs on, in `writer-defect-and-guarantee`. Not covered yet: the other five kinds; a request that states a decision is
accepted with nothing open, which should give `Accepted`; a check in a repository without a guide; a machine check from
**Confirmation** that ran and passed; a `Proposed` rule that replaces an accepted one under a guide that makes
`Proposed` records bind; a repository where `apm compile` renders `AGENTS.md`, so that the paragraph for the agent that
writes code goes into `.apm/instructions/`; a defect that departs from an accepted record rather than a convention; a
departure with a recorded reason, which is no defect; a rewrite or a superseding record that keeps a rule the code does
not meet; and a departure that the user calls deliberate, or a rule the user asks for after the defect is named, which
should each give a rule.

`coder-trailers` lists in its `skills` file the skills its session reads instead of `adr-authoring`, and holds a
`prompt-baseline.md` that `--baseline` answers with the same skills; `run-case.sh` says how.

## The cases

| Case | Side | Rules |
| --- | --- | --- |
| [`checker-partial-delivery`](checker-partial-delivery/README.md) | checker | `Implements` claims every case; a deferral leaves only the altered cases judged |
| [`checker-open-point`](checker-open-point/README.md) | checker | a check deleted under an open point is `Violates`; an allowance the open point decides is `Cannot tell` |
| [`checker-proposed-replacement`](checker-proposed-replacement/README.md) | checker | a `Proposed` record gets an advisory line and no verdict; an untouched deferred rule is `Deferred` |
| [`checker-structural`](checker-structural/README.md) | checker | an import across a structural rule is `Violates`, also in a package that already failed it; an import in the other direction touches no rule |
| [`checker-proposed-binding`](checker-proposed-binding/README.md) | checker | under a guide that makes `Proposed` records bind, an `Implements` entry for a `Proposed` rule counts |
| [`writer-vague-notes`](writer-vague-notes/README.md) | writer | a placeholder and an open point for a value the notes leave open; the guide is asked about before it is added |
| [`writer-structural`](writer-structural/README.md) | writer | a structural rule tagged with the code it constrains and its check named; records of another template; the guide and the paragraph for the agent that writes code |
| [`writer-accepted-record`](writer-accepted-record/README.md) | writer | an added requirement goes into a new record; a broken link is fixed in place |
| [`writer-two-decisions`](writer-two-decisions/README.md) | writer | two decisions get a proposed split; one decision stays one record |
| [`writer-defect-and-guarantee`](writer-defect-and-guarantee/README.md) | writer | a defect fix becomes a proposed Bug that the record does not name, not a rule or an open point; a base image's guarantee is a fact in Context; a decision stays a rule where the code does not meet it yet or a dependency already provides it |
| [`coder-trailers`](coder-trailers/README.md) | agent that writes code | the paragraph in `AGENTS.md` leads to the trailers; a partial delivery is deferred |
