# Case: a structural rule against an import

The input is one accepted record, ADR-0012, with two structural rules: no package under `internal/token/` imports a
package under `internal/http/` (R1) or `net/http` (R2). Its **Confirmation** names a depguard rule whose result the
checker cannot see, so both rules stay in the walk. Change A adds an import of `internal/http/problem` to a token
package: R1 `Violates`, and R2, which no import of `net/http` reaches, is not touched. Change B is the noise input: it
adds an import in the other direction, from an HTTP package to a token package, and touches neither rule. Change C adds
a forbidden import to a package that already had one: R1 `Violates`, since the new import is a relation the invariant
forbids, and the older import is named apart.

## Skill parts

- `SKILL.md`: "Rules" (**Form**, the structural rule; **Layer**), "Confirmation and implementation notes", "Checking a
  change" (step 2: the layers a change touches; step 3: a machine check whose result cannot be seen; the verdict table;
  the paragraph on cases, a case of a structural rule)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **A violates R1.** In Change A, ADR-0012 R1 gets `Violates`.
2. **R2 untouched in A.** ADR-0012 R2, if walked, is never `Conforms`, `Violates`, or `Cannot tell` in Change A.
3. **R1 untouched in B.** ADR-0012 R1, if walked, is never `Conforms`, `Violates`, or `Cannot tell` in Change B: the
   change alters no import of a token package.
4. **R2 untouched in B.** The same for ADR-0012 R2.
5. **C violates R1.** In Change C, ADR-0012 R1 gets `Violates`, though the package failed R1 before the change.
6. **R2 untouched in C.** ADR-0012 R2, if walked, is never `Conforms`, `Violates`, or `Cannot tell` in Change C.
7. **Older violation named.** Change C's report names the import of `internal/http/auth` apart from the verdicts: a
   defect in code the change leaves alone.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-structural opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-structural
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/r2-conforms-on-bf6c2035.md` is `sonnet/result.md` as run on tree `bf6c2035`, before Change C entered the
input, which gives ADR-0012 R2 `Conforms` in Change A; it fails check 2, and checks 5 and 7, since it has no Change C.
`controls/b-judged.md` is the same result with Change B giving both rules `Conforms` and a Change C that gives R2
`Conforms` and names no older violation; it fails checks 2, 3, 4, 6, and 7.

## Results

Runs of 2026-11-11 on tree `025f4b62`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. All four results pass all seven checks. Change A gives ADR-0012 R1 `Violates` and R2 `Not
touched`. Change B leaves both rules out of the walk or `Not touched`, since it changes only the `http` layer. Change C
gives R1 `Violates` for the new import of `internal/http/admin`, R2 `Not touched`, and names the older import of
`internal/http/auth` apart ("Failed before this change and left as it was").

Earlier rounds failed check 2 on Sonnet, before Change C was added. On tree `bf6c2035`, both Sonnet results gave R2
`Conforms` in Change A ("The new file in the token layer does not import `net/http`"): the skill did not say what a case
of a structural rule is. Tree `ff1e39aa` made each unit the invariant ranges over a case, and both Sonnet results still
gave `Conforms`. Tree `6c8380e9` added that a file added to a package that meets the invariant before and after the
change alters no outcome, and both Sonnet runs then gave `Not touched`. Review of tree `7aeb0ec4` found that a unit-only
definition gives a new forbidden import in a package that already failed `Not touched`; tree `9fb67955` makes each
forbidden relation a case of its own, and Change C tests it. Tree `025f4b62` words that sentence more precisely, and the
results above ran on it. Opus gave `Not touched` for R2 in every round.

The baselines ran on 2026-11-11 with `english-developer-style` alone, on the input with Change C. Both say "violated"
for R1 in Changes A and C, which matches in meaning, and judge no rule in Change B. Both fail checks 1 and 5 on the word
only and pass the others.

Tree `3b230c74` changes only the bullet on named sets under "Terms" and rule R3 of the example record, so that neither
asks for an approver as a rule. No input of this case has a set that is expected to change, and no result of it writes a
named set, an approval rule, or a `CODEOWNERS` entry, though every session reads the example; the results above stand
for the tree.

Tree `d42618eb` adds three passages for the writer of a record: under "What belongs in an ADR", the sorting of a
requirement into a decision, a defect, or a guarantee of a dependency; under "Open points", that a question about a
defect gets no open point; and under "Drafting from the user's input", how such a question is answered. This case checks
changes against records that exist and writes no record, so the results above stand for the tree.

Tree `d8b52781` changes only "Rules": **One home** says when a rule cites another rule, that a citation of a rule of
another record copies none of that rule's conditions in any section, and that a rule other rules imply is left out, and
it takes in **No pointer rules**; **Every requirement is a rule** asks for a rule number instead of a record. This case
checks changes against records that exist and writes no record, so the results above stand for the tree.
