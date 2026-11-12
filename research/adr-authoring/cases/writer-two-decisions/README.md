# Case: notes with two decisions, and notes with one

The input is two requests. The first has notes with two decisions that different people settle (token verification by
the security architect, a liveness endpoint by the platform team); the skill writes at most one record and proposes the
split. The second has notes with three choices that one authority settles and that change together, which are one
decision and one record. Request 2 is the noise input for the split rule.

## Skill parts

- `SKILL.md`: "What belongs in an ADR" (one decision per record, split no further, propose the split); "Terms" (a named
  set for the trusted key sources, a set that is expected to change; no check reads it)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **At most one record.** Request 1 writes at most one record file.
2. **Split proposed.** Request 1's message proposes a separate record for the other decision; a sentence that denies a
   split does not count.
3. **One record.** Request 2 writes exactly one record file.
4. **No split.** Request 2's message proposes no split.
5. **No guide written.** Neither request writes a `README.md`: the repository has its guide.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-two-decisions opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-two-decisions
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/split-one-decision.md` is `opus/result.md` with a second record and a proposed split added to Request 2; it
fails checks 3 and 4. `controls/merged-no-split.md` is `opus/result.md` with the message of Request 1 replaced by "Both
choices are in one record, and there is no need to split them."; it fails check 2. `controls/guide-rewritten.md` is
`opus/result.md` with a `README.md` added to Request 1; it fails the guide check.

## Results

Runs of 2026-11-11 on tree `d42618eb`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because "What belongs in an ADR" now sorts each
requirement into a decision, a defect, or a guarantee of a dependency, "Open points" gives a question about a defect no
open point, and "Drafting from the user's input" says how such a question is answered. Every requirement of the notes is
a decision, so the new passages have to stay quiet. All four results pass all five checks: Request 1 writes ADR-0006 for
the security architect's decision alone and offers a separate record for the health endpoint, and Request 2 writes one
record for the three choices and proposes no split. No result names a defect or proposes an issue.

The previous rounds, on trees `3b230c74` and `bf6c2035`, passed the same way. The intermediate trees of this change,
`89cbfb4e` to `1db689e3`, ran this case as well and passed by meaning; their results are not kept.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since. Both write two
records for Request 1 without asking ("I split the notes into two ADRs"), which fails check 1 and, by meaning, check 2.

Tree `d8b52781` changes only "Rules": **One home** says when a rule cites another rule, that a citation of a rule of
another record copies none of that rule's conditions in any section, and that a rule other rules imply is left out, and
it takes in **No pointer rules**; **Every requirement is a rule** asks for a rule number instead of a record. This case
writes records, but its skill parts list no part of "Rules", and its inputs hold no rule of another record, so the
results above stand for the tree.
