# Case: a deleted check and an allowance under an open point

The input is one rule, ADR-0007 R4 (an expired token gets 401), under an open point that lists two answers for the
clock-skew allowance, 0 and 30 seconds. Change A deletes the expiry check, so a token expired an hour ago passes under
either answer: `Violates`. Change B adds a 30-second allowance, which meets R4 under one answer and fails it under the
other: `Cannot tell`. B is the noise input for the rule that `Violates` wins where every answer fails.

## Skill parts

- `SKILL.md`: "The reading guide" (the verdict table with readings and answers, the judging paragraph), "Open points"
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **A violates.** In Change A, ADR-0007 R4 gets `Violates`.
2. **B cannot tell.** In Change B, ADR-0007 R4 gets `Cannot tell`.
3. **R5 untouched in A.** ADR-0007 R5, if walked, is never `Conforms`, `Violates`, or `Cannot tell`.
4. **R5 untouched in B.** The same for Change B.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-open-point opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-open-point
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/r5-judged.md` is `opus/result.md` with a row that gives ADR-0007 R5 `Conforms` in both changes; it fails
checks 3 and 4. `controls/wrong-verdicts.md` is `opus/result.md` with R4 given `Cannot tell` in Change A and `Violates`
in Change B; it fails checks 1 and 2.

## Results

Runs of 2026-11-09 on tree `61999f9e` (the skill at a49f24d), graded by reading; both models at the default effort. "r1"
and "r2" are `result.md` and `result-2.md`. All four results pass all four checks: Change A gives ADR-0007 R4
`Violates`, since a token expired an hour ago passes under both answers O1 lists, and Change B gives it `Cannot tell`,
since 30 seconds meets R4 under one answer and fails it under the other. Opus leaves R5 out of the walk; Sonnet lists it
as `Not touched`. As in `checker-partial-delivery`, an earlier input left R4 and R5 without a precedence for a token
with no `kid`; R4 now covers only a token that has one.

The baselines ran the same day with `english-developer-style` alone. They say "fails" or "violated" for Change A and
"undecided, waiting on O1" or "undecided, blocked on O1" for Change B. Both fail checks 1 and 2 on the words only: the
meaning matches both expected verdicts.
