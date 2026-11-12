# Case: a partial delivery against a `Proposed` record that binds

The input is `checker-partial-delivery` with two differences: ADR-0007 is `Proposed`, and the reading guide makes
`Proposed` and `Accepted` records bind a change in this repository. A trailer entry that names a rule of a binding
`Proposed` record counts like any other, so Change A, whose `Implements` claims the unknown-`kid` case of R5 that the
change leaves wrong, gets `Violates`, and Change B, which defers R5 to #12, gets `Conforms` with the deferral named. A
reading that drops every entry naming a `Proposed` rule gives Change A `Conforms`. Change B is the noise input, as in
`checker-partial-delivery`.

## Skill parts

- `SKILL.md`: "Checking a change" (step 1: an entry that names a `Proposed` rule that binds the change; step 4: which
  `Proposed` rules bind nothing; the verdict table, a case, touching, the judging paragraph), "The reading guide" (a
  guide that makes `Proposed` records bind), "Delivery stays out of the record" (`Implements` claims every case)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **A violates.** In Change A, ADR-0007 R5 gets `Violates`: the `Implements` entry counts, though ADR-0007 is
   `Proposed`.
2. **B conforms.** In Change B, ADR-0007 R5 gets `Conforms`.
3. **B names the deferral.** Change B's report names the deferral to #12.
4. **R4 untouched in A.** ADR-0007 R4, if walked, is `Not touched` or `Deferred` in Change A.
5. **R4 untouched in B.** The same for Change B.
6. **No advisory line.** No line says `would violate ADR-0007 R5`: the rule binds, so it gets a verdict instead.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/checker-proposed-binding opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/checker-proposed-binding
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/dropped-entry.md` is `opus/result.md` with ADR-0007 R5 given `Conforms` in Change A, as if the `Implements`
entry for a `Proposed` rule counted for nothing, and a line `would violate ADR-0007 R5`; it fails checks 1 and 6.
`controls/r4-judged-no-deferral.md` is `opus/result.md` with R4 given `Conforms` in both changes and every line about
the deferral removed from Change B; it fails checks 2 to 5.

## Results

Runs of 2026-11-11 on tree `025f4b62`, graded by reading; both models at the default effort. "r1" to "r4" are
`result.md` to `result-4.md`. In every result, Change A gives ADR-0007 R5 `Violates`, since its `Implements` entry
counts though ADR-0007 is `Proposed`, R4 is `Not touched` in both changes, and no result writes an advisory line for R5.
Both Opus results and Sonnet r1 pass all six checks. Sonnet r2 fails check 2: it gives R5 `Violates` in Change B because
the unknown-`kid` case still gets `TOKEN_INVALID`, a case the change leaves as it was and names under `Defers`. Sonnet
r3 and r4, run to see how often that happens, pass all six checks, so Sonnet passes in three of four runs. On the same
input with an `Accepted` record, `checker-partial-delivery`, Sonnet has passed check 2 in every round.

The baselines ran on 2026-11-11 with `english-developer-style` alone. Opus says "fail" for Change A and "deferred" for
Change B; Sonnet says "violated" and "deferred". Both fail checks 1 and 2 on the words, where Sonnet's Change A matches
in meaning, and check 2 on the meaning too: neither judges Change B by the case it alters.

Tree `3b230c74` changes only the bullet on named sets under "Terms" and rule R3 of the example record, so that neither
asks for an approver as a rule. No input of this case has a set that is expected to change, and no result of it writes a
named set, an approval rule, or a `CODEOWNERS` entry, though every session reads the example; the results above stand
for the tree.

Tree `d42618eb` adds three passages for the writer of a record: under "What belongs in an ADR", the sorting of a
requirement into a decision, a defect, or a guarantee of a dependency; under "Open points", that a question about a
defect gets no open point; and under "Drafting from the user's input", how such a question is answered. This case checks
changes against records that exist and writes no record, so the results above stand for the tree.
