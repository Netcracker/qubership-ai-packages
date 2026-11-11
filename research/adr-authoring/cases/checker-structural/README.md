# Case: a structural rule against an import

The input is one accepted record, ADR-0012, with two structural rules: no package under `internal/token/` imports a
package under `internal/http/` (R1) or `net/http` (R2). Its **Confirmation** names a depguard rule whose result the
checker cannot see, so both rules stay in the walk. Change A adds an import of `internal/http/problem` to a token
package: R1 `Violates`, and R2, which no import of `net/http` reaches, is not touched. Change B is the noise input: it
adds an import in the other direction, from an HTTP package to a token package, and touches neither rule.

## Skill parts

- `SKILL.md`: "Rules" (**Form**, the structural rule; **Layer**), "Confirmation and implementation notes", "Checking a
  change" (step 2: the layers a change touches, a rule whose machine check cannot be seen stays in the walk; the verdict
  table)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **A violates R1.** In Change A, ADR-0012 R1 gets `Violates`.
2. **R2 untouched in A.** ADR-0012 R2, if walked, is never `Conforms`, `Violates`, or `Cannot tell` in Change A.
3. **R1 untouched in B.** ADR-0012 R1, if walked, is never `Conforms`, `Violates`, or `Cannot tell` in Change B: the
   change alters no import of a token package.
4. **R2 untouched in B.** The same for ADR-0012 R2.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-structural opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-structural
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/r2-conforms-on-bf6c2035.md` is `sonnet/result.md` as run on tree `bf6c2035`, which gives ADR-0012 R2
`Conforms` in Change A; it fails check 2. `controls/b-judged.md` is the same result with Change B giving both rules
`Conforms`; it fails checks 2, 3, and 4.

## Results

Runs of 2026-11-11 on tree `7aeb0ec4`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. All four results pass all four checks: Change A gives ADR-0012 R1 `Violates` and R2 `Not
touched`, and Change B leaves both rules `Not touched`, since it changes only the `http` layer and no import of a token
package.

Two earlier rounds failed check 2 on Sonnet. On tree `bf6c2035`, both Sonnet results gave R2 `Conforms` in Change A
("The new file in the token layer does not import `net/http`"): the skill did not say what a case of a structural rule
is. Tree `ff1e39aa` made each unit the invariant ranges over a case, and both Sonnet results still gave `Conforms`. Tree
`6c8380e9` adds that a file added to a package that meets the invariant before and after the change alters no outcome,
and both Sonnet runs then gave `Not touched`. Tree `7aeb0ec4` gives that rule the condition that no other unit's outcome
changes; all four results above ran on it. Opus gave `Not touched` in every round.

The baselines ran on 2026-11-11 with `english-developer-style` alone. Both say "violated" for R1 in Change A, which
matches in meaning, and judge no rule in Change B. Both fail check 1 on the word only and pass checks 2 to 4.
