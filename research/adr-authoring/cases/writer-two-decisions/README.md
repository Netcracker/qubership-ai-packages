# Case: notes with two decisions, and notes with one

The input is two requests. The first has notes with two decisions that different people settle (token verification by
the security architect, a liveness endpoint by the platform team); the skill writes at most one record and proposes the
split. The second has notes with three choices that one authority settles and that change together, which are one
decision and one record. Request 2 is the noise input for the split rule.

## Skill parts

- `SKILL.md`: "What belongs in an ADR" (one decision per record, split no further, propose the split)
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

Runs of 2026-11-09 on tree `61999f9e` (the skill at a49f24d), graded by reading; both models at the default effort. "r1"
and "r2" are `result.md` and `result-2.md`. All four results pass all five checks: Request 1 writes ADR-0006 for the
security architect's decision alone and offers ADR-0007 for the health endpoint, and Request 2 writes one record for the
three choices and proposes no split. Sonnet r1 was run again the same day, because the first run's message referred to
the address of the account that ran it; no result names an address.

The baselines ran the same day with `english-developer-style` alone. Both write two records for Request 1 without asking
("I split the notes into two ADRs"), which fails check 1 and, by meaning, check 2.
