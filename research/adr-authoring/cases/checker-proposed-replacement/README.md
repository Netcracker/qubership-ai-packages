# Case: a `Defers` line that names a `Proposed` replacement

The input is an accepted rule, ADR-0010 R7 (keys reload after 5 minutes), a `Proposed` record whose R3 replaces it
(1 minute), and a change that deletes the expiry of the key set while its `Defers` names ADR-0020 R3 and ADR-0010 R9.
A replacing rule binds nothing until its record is accepted, so R7 governs and gets `Violates`, and the `Defers` entry
for R3 counts for nothing. ADR-0010 R9 is untouched, unmet, and deferred to an open issue: `Deferred`, the noise input
for the rule that a deferral cannot hide a touched rule.

## Skill parts

- `SKILL.md`: "The reading guide" (step 1 and step 2: a `Proposed` replacement binds nothing until accepted; the verdict
  table), "Local conventions" (superseding part of a record), "Delivery stays out of the record" (a `Defers` target)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **R7 violates.** ADR-0010 R7 gets `Violates`.
2. **R9 deferred.** ADR-0010 R9 gets `Deferred`.
3. **R3 gets no verdict.** ADR-0020 R3 gets none of the five verdicts: it binds nothing until ADR-0020 is accepted.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-proposed-replacement opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-proposed-replacement
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/r3-judged.md` is `opus/result.md` with a row that gives ADR-0020 R3 `Deferred`; it fails check 3.
`controls/wrong-verdicts.md` is `opus/result.md` with R7 given `Conforms` and R9 `Not touched`; it fails checks 1 and 2.

## Results

Runs of 2026-11-09 on tree `61999f9e` (the skill at a49f24d), graded by reading; both models at the default effort. "r1"
and "r2" are `result.md` and `result-2.md`. All four results pass all three checks: ADR-0010 R7 gets `Violates`,
ADR-0010 R9 gets `Deferred`, and ADR-0020 R3 gets no verdict. Each says that R3 binds nothing until ADR-0020 is accepted
and that the `Defers` entry for it counts for nothing. An earlier round on the same day used an R9 about HTTP 5xx
answers to a reload, which the change made impossible to reach; R9 is now the load at startup, which the change leaves
alone.

The baselines ran the same day with `english-developer-style` alone. Both say "Violated" for R7, which matches in
meaning, and both treat R3 as not in force ("Not in force", "Not binding; deferred to #300"). For R9, Opus says
"Violated, deferred to issue #301", which judges an untouched rule, and Sonnet says "not met before the change,
unchanged by it; deferred to #301", which matches `Deferred` in meaning. Both fail checks 1 and 2 on the words, and Opus
fails check 2 on the meaning too.
