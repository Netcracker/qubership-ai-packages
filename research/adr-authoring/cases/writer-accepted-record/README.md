# Case: an added requirement and a broken link in an accepted record

The input is an accepted record, ADR-0007, and two requests handled apart: add a requirement, and fix a broken link.
The skill puts a requirement added to an accepted record into a new record, links the old one back only when the new
one is accepted, and tells the user that the accepted record stays as it is. A broken link is an editorial fix that the
accepted record takes in place. Request 2 is the noise input for the rule that an accepted record is not edited.

## Skill parts

- `SKILL.md`: "Local conventions" (immutability and the edits an accepted record takes, superseding part of a record),
  "Template", "Rules" (**One home**, a citation of a rule of another record by what the rule is about, which no check
  reads here: the new rule of Request 1 can refuse a token that ADR-0007 R4 or R5 refuses too, so the record states
  which one wins (**Precedence**), and the shape of a precedence over a rule of another record is the question of issue
  #278)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **New record.** Request 1 writes `docs/adr/0008-<slug>.md` with a rule that carries `TOKEN_ALG_NONE` and names
   ADR-0007.
2. **ADR-0007 untouched.** Request 1 leaves ADR-0007 as it is: no file, or the same text.
3. **User told.** Request 1's message says that the accepted record stays as it is, and ADR-0007 is not edited.
4. **Only the link fixed.** Request 2 gives ADR-0007 with the link to `0006-trusted-key-sources.md` and every other line
   as it was.
5. **No new record.** Request 2 writes no other record.
6. **No guide written.** Neither request writes a `README.md`: the repository has its guide, so this is the noise input
   for the rule that the first record adds one.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-accepted-record opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-accepted-record
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/edits-and-extra-record.md` is the Opus r1 of tree `d42618eb` with the sentences about ADR-0007 staying as it
is removed from Request 1, another line of ADR-0007 changed in Request 2, and a record 0009 added there; it fails checks
3, 4, and 5. `controls/guide-rewritten.md` is the same result with a `README.md` added to Request 1; it fails the guide
check.

## Results

Runs of 2026-11-25 on tree `ad64edef`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because "Rules" now asks for a citation of a rule of
another record by what the rule is about, in every section, and Request 1 cites ADR-0007 R4 and R5. All four results
pass all six checks: Request 1 writes a `Proposed` ADR-0008 with a `TOKEN_ALG_NONE` rule that names ADR-0007, links
ADR-0007 under **Related ADRs**, leaves ADR-0007 as it is, and says so; Request 2 fixes the link and changes no other
line; neither writes a guide. Each R1 states a precedence over ADR-0007 R4 and R5: Opus r1 and Opus r2 yield to them,
and Sonnet r1 and Sonnet r2 let `TOKEN_ALG_NONE` win. Each plans a line in ADR-0007 for ADR-0008 once ADR-0008 is
accepted. Opus r1, Sonnet r1, and Sonnet r2 name a reason code of ADR-0007 R4 or R5 where they state the precedence,
which **One home** asks them to cite by what the rule is about. How a later record excepts or overrides an accepted
rule, and which lines that leaves, is the question of
[Netcracker/qubership-ai-packages#278](https://github.com/Netcracker/qubership-ai-packages/issues/278), and no check of
this case reads it. On `3b37f1b0`, a tree of the same day whose results this commit replaces, all four also passed all
six checks, and all four let `TOKEN_ALG_NONE` win.

Trees `88a72faf` and `dc50203b` differ from `ad64edef` only in the guarantee of a dependency under "What belongs in an
ADR": `88a72faf` states it in Context as a fact only where its source has no rules, and `dc50203b` only where its source
is not a decision record. The inputs of this case hold no guarantee of a dependency, so the results above stand for
both trees.

On tree `d42618eb`, before this change, the case ran because "What belongs in an ADR" began to sort each requirement
into a decision, a defect, or a guarantee of a dependency, and the requirement added to ADR-0007 is a decision. All four
results passed all six checks: Request 1 wrote a `Proposed` ADR-0008 with a `TOKEN_ALG_NONE` rule that named ADR-0007,
left ADR-0007 as it was, and said so; Request 2 fixed the link and changed no other line; neither wrote a guide. All
four raised the letter case of `none` and the precedence over ADR-0007 R4 and R5 as open points, and Sonnet r1 also made
the precedence a rule. No result named a defect or proposed an issue.

Before that, on tree `bf6c2035`, Sonnet r2 made the precedence a rule, and Opus r2 and Sonnet r2 said that the guide
puts `docs/adr/` in no layer, which the input does not state. The intermediate trees of that change, `89cbfb4e` to
`1db689e3`, ran this case as well and passed; their results are not kept.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since. Opus passes all
six checks without the skill, though it offers to move the rule into ADR-0007 instead. Sonnet fails checks 1, 2, and 3:
it adds the rule to ADR-0007 in place as R6 and writes no new record.
