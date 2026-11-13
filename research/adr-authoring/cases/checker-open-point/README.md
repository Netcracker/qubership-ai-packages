# Case: a deleted check and an allowance under an open point

The input is one rule, ADR-0007 R4 (an expired token gets 401), under an open point that lists two answers for the
clock-skew allowance, 0 and 30 seconds. Change A deletes the expiry check, so a token expired an hour ago passes under
either answer: `Violates`. Change B adds a 30-second allowance, which meets R4 under one answer and fails it under the
other: `Cannot tell`. B is the noise input for the rule that `Violates` wins where every answer fails.

## Skill parts

- `SKILL.md`: "Checking a change" (the verdict table with readings and answers, the judging paragraph), "The reading
  guide" (a guide that makes `Proposed` records bind), "Open points"
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

Runs of 2026-11-11 on tree `025f4b62`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The input now carries a reading guide that makes `Proposed` records bind in this
repository, which the skill otherwise does not, so the case also runs that switch. All four results pass all four
checks: Change A gives ADR-0007 R4 `Violates`, since a token expired an hour ago passes under both answers O1 lists, and
Change B gives it `Cannot tell`, since 30 seconds meets R4 under one answer and fails it under the other. All four list
R5 as `Not touched`. As in `checker-partial-delivery`, an earlier input left R4 and R5 without a precedence for a token
with no `kid`; R4 now covers only a token that has one.

The baselines ran on 2026-11-11 with `english-developer-style` alone, on the input with the guide. They say "violated"
for Change A, and "undecided (O1)" or "open, depends on O1" for Change B. Both fail checks 1 and 2 on the words only:
the meaning matches both expected verdicts.

Tree `3b230c74` changes only the bullet on named sets under "Terms" and rule R3 of the example record, so that neither
asks for an approver as a rule. No input of this case has a set that is expected to change, and no result of it writes a
named set, an approval rule, or a `CODEOWNERS` entry, though every session reads the example; the results above stand
for the tree.

Tree `d42618eb` adds three passages for the writer of a record: under "What belongs in an ADR", the sorting of a
requirement into a decision, a defect, or a guarantee of a dependency; under "Open points", that a question about a
defect gets no open point; and under "Drafting from the user's input", how such a question is answered. This case checks
changes against records that exist and writes no record, so the results above stand for the tree.

Tree `b7a46b78` changes only "Rules": **Numbers freeze** asks for a link under **Related ADRs** to every cited record;
**One home** says when a rule cites another rule, that a citation of a rule of another record names what that rule is
about and none of what it decides, that a rule other rules imply is left out, and that a case a rule of another record
leaves unclear belongs to that record, and it takes in **No pointer rules**; **Every requirement is a rule** asks for a
rule number instead of a record. This case checks changes against records that exist and writes no record, so the
results above stand for the tree.

Tree `8fe854e2` adds to the contents of the guide, under "The reading guide", that the agent that writes code reads the
**Related ADRs** of a record that a rule cites. This case checks changes against records and a guide that exist, and
writes neither, so the results above stand for that tree as well.
