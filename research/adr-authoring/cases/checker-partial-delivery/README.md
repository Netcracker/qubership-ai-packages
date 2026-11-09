# Case: a partial delivery under `Implements` and under `Defers`

The input is one change to a rule with two cases, ADR-0007 R5 (a token with no `kid` and a token whose `kid` names no
loaded key). The change makes the first case right and leaves the second wrong. Change A names R5 under `Implements`,
change B names it under `Defers` with an existing issue. The skill judges every case of a rule named under `Implements`,
so A gets `Violates`; under `Defers` it judges only the cases the change alters, so B gets `Conforms`, with the deferral
named beside it. B is the noise input for the `Implements` rule.

## Skill parts

- `SKILL.md`: "The reading guide" (the verdict table, a case, touching, the judging paragraph), "Delivery stays out of
  the record" (`Implements` claims every case)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **A violates.** In Change A, ADR-0007 R5 gets `Violates`: `Implements` puts the unknown-`kid` case under judgment,
   and the change leaves it wrong.
2. **B conforms.** In Change B, ADR-0007 R5 gets `Conforms`: the only case the change alters is right.
3. **B names the deferral.** Change B's report names the deferral to #12.
4. **R4 untouched in A.** ADR-0007 R4, if walked, is `Not touched` or `Deferred`, never `Conforms`, `Violates`, or
   `Cannot tell`: the change alters no outcome of R4.
5. **R4 untouched in B.** The same for Change B.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-partial-delivery opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-partial-delivery
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/r4-judged-no-deferral.md` is `opus/result.md` with a row that gives ADR-0007 R4 `Conforms` in both changes and
every mention of the deferral removed; it fails checks 3, 4, and 5. `controls/wrong-verdicts.md` is `opus/result.md`
with R5 given `Conforms` in Change A and `Deferred` in Change B, the skill's own words for the wrong answers; it fails
checks 1 and 2.

## Results

Runs of 2026-11-09 on tree `61999f9e` (the skill at a49f24d), graded by reading; both models at the default effort. "r1"
and "r2" are `result.md` and `result-2.md`. All four results pass all five checks: Change A gives ADR-0007 R5 `Violates`
because `Implements` claims the unknown-`kid` case the change leaves wrong, and Change B gives it `Conforms`, with the
deferral to #12 named beside it. Opus leaves R4 out of the walk, since no guide maps a layer and no R4 case changes;
Sonnet lists it as `Not touched`.

An earlier round the same day ran an input in which R4 and R5 both described an expired token with no `kid` and said
nothing about which wins. Three of four results then gave Change B `Cannot tell` and named the missing precedence, which
the skill's **Precedence** rule asks a record to state. The input now puts that exception inside R5, and the runs above
are on that input.

The baselines ran the same day with `english-developer-style` alone. Opus says "fail" for Change A and "deferred" for
Change B; Sonnet says "violated" and "partly met, rest deferred". Both fail check 1 on the word, while the meaning
matches, and check 2 on the meaning: neither judges Change B by the case the change alters.
