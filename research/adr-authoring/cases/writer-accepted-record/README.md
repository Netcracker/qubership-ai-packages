# Case: an added requirement and a broken link in an accepted record

The input is an accepted record, ADR-0007, and two requests handled apart: add a requirement, and fix a broken link.
The skill puts a requirement added to an accepted record into a new record, links the old one back only when the new
one is accepted, and tells the user that the accepted record stays as it is. A broken link is an editorial fix that the
accepted record takes in place. Request 2 is the noise input for the rule that an accepted record is not edited.

## Skill parts

- `SKILL.md`: "Local conventions" (immutability and the edits an accepted record takes, superseding part of a record),
  "Template", "Rules" (**One home**: a precedence over a rule of another record keeps its citation; no check reads the
  citations of Context)
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

`controls/edits-and-extra-record.md` is `opus/result.md` with the sentences about ADR-0007 staying as it is removed from
Request 1, another line of ADR-0007 changed in Request 2, and a record 0009 added there; it fails checks 3, 4, and 5.
`controls/guide-rewritten.md` is `opus/result.md` with a `README.md` added to Request 1; it fails the guide check.

## Results

Runs of 2026-11-12 on tree `d8b52781`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because **One home** now says when a rule cites a rule
of another record, and the new record has to say how R1 relates to ADR-0007 R4 and R5, so the citation has to stay.
All four results pass all six checks: Request 1 writes a `Proposed` ADR-0008 with a `TOKEN_ALG_NONE` rule that names
ADR-0007, leaves ADR-0007 as it is, and says so; Request 2 fixes the link and changes no other line; neither writes a
guide. Each writes the precedence over ADR-0007 R4 and R5 into R1, with `TOKEN_ALG_NONE` winning, and cites those rules
by number, three of them by subject as well, such as "the `kid` check of ADR-0007 R5". No Context says what ADR-0007 R4
or R5 accepts or refuses. Where a Negative consequence names the reason code that ADR-0007 R4 or R5 gave before, it
names the answer this record replaces, which **One home** allows.

On tree `d42618eb`, before this change, the four results passed all six checks as well; there all four raised the
precedence as an open point, and Sonnet r1 also made it a rule.

In the round before, on tree `bf6c2035`, Sonnet r2 made the precedence a rule, and Opus r2 and Sonnet r2 said that the
guide puts `docs/adr/` in no layer, which the input does not state. The intermediate trees between `bf6c2035` and
`d42618eb`, `89cbfb4e` to `1db689e3`, ran this case as well and passed, and so did `ba170d99`, an earlier tree of this
change; their results are not kept.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since. Opus passes all
six checks without the skill, though it offers to move the rule into ADR-0007 instead. Sonnet fails checks 1, 2, and 3:
it adds the rule to ADR-0007 in place as R6 and writes no new record.
