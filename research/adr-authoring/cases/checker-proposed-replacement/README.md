# Case: a `Defers` line that names a `Proposed` replacement

The input is an accepted rule, ADR-0010 R7 (keys reload after 5 minutes), a `Proposed` record whose R3 replaces it (1
minute), and a change that deletes the expiry of the key set while its `Defers` names ADR-0020 R3 and ADR-0010 R9. The
guide makes only `Accepted` records bind a change, so R7 governs and gets `Violates`, the `Defers` entry for R3 counts
for no verdict and is no error, and R3 gets the advisory line `would violate ADR-0020 R3`. ADR-0010 R9 is untouched,
unmet, and deferred to an open issue: `Deferred`, the noise input for the rule that a deferral cannot hide a touched
rule.

## Skill parts

- `SKILL.md`: "Checking a change" (step 1: an entry that names a `Proposed` rule; step 4: the advisory line; the
  verdict table), "The reading guide" (which statuses bind), "Local conventions" (superseding part of a record),
  "Delivery stays out of the record" (a `Defers` target)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **R7 violates.** ADR-0010 R7 gets `Violates`.
2. **R9 deferred.** ADR-0010 R9 gets `Deferred`.
3. **R3 gets no verdict.** ADR-0020 R3 gets none of the five verdicts: the guide makes only `Accepted` records bind a
   change.
4. **Advisory line.** The report carries the line `would violate ADR-0020 R3`, since the change, which deletes the
   expiry, fails R3 under every reading.
5. **No trailer error.** The report does not list the `Defers` entry for ADR-0020 R3 as a trailer error: an entry that
   names a rule of a `Proposed` record counts for no verdict and is not an error.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-proposed-replacement opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-proposed-replacement
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/r3-judged.md` is `opus/result.md` as run on tree `61999f9e`, with a row that gives ADR-0020 R3 `Deferred`; it
fails checks 3 and 4. `controls/wrong-verdicts.md` is the same result with R7 given `Conforms` and R9 `Not touched`; it
fails checks 1, 2, and 4. Neither of those results carries the advisory line, which the skill at `61999f9e` did not ask
for. `controls/proposed-entry-as-error.md` is `opus/result.md` as run on tree `6c8380e9`, with the `Defers` entry for
ADR-0020 R3 listed under "Trailer errors"; it fails check 5.

## Results

Runs of 2026-11-11 on tree `7aeb0ec4`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The guide in the input makes only `Accepted` records bind. All four results pass all five
checks: ADR-0010 R7 gets `Violates`, ADR-0010 R9 gets `Deferred`, ADR-0020 R3 gets no verdict and the line `would
violate ADR-0020 R3`, and the `Defers` entry for R3 counts for no verdict and is not listed as a trailer error. An
earlier round on 2026-11-09 used an R9 about HTTP 5xx answers to a reload, which the change made impossible to reach; R9
is now the load at startup, which the change leaves alone.

The baselines ran on 2026-11-11 with `english-developer-style` alone, on the input with the guide. Both say "violated"
for R7, which matches in meaning. For R9, Opus says "violated, pre-existing" and Sonnet "violated", which judge an
untouched rule, and neither writes the advisory line for R3. Both fail checks 1, 2, and 4 on the words, and checks 2 and
4 on the meaning too.
