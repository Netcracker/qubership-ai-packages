# Case: an added requirement and a broken link in an accepted record

The input is an accepted record, ADR-0007, and two requests handled apart: add a requirement, and fix a broken link.
The skill puts a requirement added to an accepted record into a new record, links the old one back only when the new
one is accepted, and tells the user that the accepted record stays as it is. A broken link is an editorial fix that the
accepted record takes in place. Request 2 is the noise input for the rule that an accepted record is not edited.

## Skill parts

- `SKILL.md`: "Local conventions" (immutability and the edits an accepted record takes, superseding part of a record),
  "Template"
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

Runs of 2026-11-09 on tree `61999f9e` (the skill at a49f24d), graded by reading; both models at the default effort. "r1"
and "r2" are `result.md` and `result-2.md`. All four results pass all six checks: Request 1 writes ADR-0008 with a
`TOKEN_ALG_NONE` rule that names ADR-0007, leaves ADR-0007 as it is, and says so ("I haven't changed ADR-0007. It is
accepted"); Request 2 fixes the link and changes no other line; neither writes a guide.

The baselines ran the same day with `english-developer-style` alone. Opus passes all six checks without the skill.
Sonnet fails checks 1, 2, and 3: it adds the rule to ADR-0007 in place as R6 and writes no new record.
