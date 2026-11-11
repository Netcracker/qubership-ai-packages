# Case: the agent that writes code finds the trailers through `AGENTS.md`

This case runs the reader that `adr-authoring` never reaches: the agent that writes code under a record. Its session
reads `change-description-authoring` and `english-developer-style`, listed in `skills`, and not `adr-authoring`. Its
input is a repository whose `AGENTS.md` carries the paragraph that "The reading guide" in `SKILL.md` asks the writer to
add, and a guide and a record the agent may consult. Change 1 brings one of the two cases of ADR-0007 R5 and leaves the
other to issue #12, so both its commit message and its description owe `Defers: ADR-0007 R5 to #12` and no `Implements:`
entry for R5. Change 2 is the noise input: a CI change under `.github/`, which belongs to no layer and owes no rule
trailer.

`prompt-baseline.md` is the same input without the paragraph in `AGENTS.md` and without the files to consult: what an
agent sees in a repository where the writer added no paragraph, since nothing else sends it to `docs/adr/`. Its results
are under `<model>/baseline/`.

## Skill parts

- `SKILL.md`: "The reading guide" (the paragraph for the agent that writes code, the guide's contents), "Delivery stays
  out of the record" (the trailers and a partial delivery under `Defers`). The session does not read `SKILL.md`; the
  input carries what it says, and `skill-tree` records the tree of `adr-authoring` the input follows.
- `change-description-authoring`: §2 (Scope, the rule trailers), §5 (the trailer table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Commit defers R5.** Change 1's commit message ends with a trailer paragraph whose `Defers:` names `ADR-0007 R5 to
   #12`, and with no `Implements:` entry for ADR-0007 R5.
2. **Description defers R5.** The same for Change 1's pull request description.
3. **No rule trailers on CI.** Neither the commit message nor the description of Change 2 has an `Implements:` or a
   `Defers:` line.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/coder-trailers opus result
research/adr-authoring/cases/run-case.sh --baseline research/adr-authoring/cases/coder-trailers opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/coder-trailers
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/ci-trailers.md` is `opus/result.md` with `Implements: ADR-0007 R4` added to the commit message and the
description of Change 2; it fails check 3.

## Results

Runs of 2026-11-11 on tree `bf6c2035` of `adr-authoring` and the `change-description-authoring` of `main`, graded by
reading; both models at the default effort. "r1" and "r2" are `result.md` and `result-2.md`. Trees `6c8380e9` and
`7aeb0ec4` change only "Checking a change", its step 4 and its paragraph on cases, which this case does not read, so
these results stand for them. All four results pass all three checks. Each ends the commit message and the description
of Change 1 with one trailer paragraph, `Defers: ADR-0007 R5 to #12`, and no other trailer, and says in the body or in
its **Scope.** paragraph that the `TOKEN_KID_UNKNOWN` case waits for #12. None puts a rule trailer on Change 2. They
mark the move from `TOKEN_INVALID` to `TOKEN_KID_MISSING` as breaking in different ways, which
`change-description-authoring` decides and no check here reads.

The baselines ran on 2026-11-11 on `prompt-baseline.md`. Both state the partial delivery in prose ("This implements part
of ADR-0007 R5, and #12 tracks the rest"; "See #12.") and end with a `BREAKING CHANGE:` footer, but carry no rule
trailer: they fail checks 1 and 2.
