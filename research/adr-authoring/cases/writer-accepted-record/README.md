# Case: an added requirement and a broken link in an accepted record

The input is an accepted record, ADR-0007, and two requests handled apart: add a requirement, and fix a broken link.
The skill puts a requirement added to an accepted record into a new record, links the old one back only when the new
one is accepted, and tells the user that the accepted record stays as it is. A broken link is an editorial fix that the
accepted record takes in place. Request 2 is the noise input for the rule that an accepted record is not edited.

## Skill parts

- `SKILL.md`: "Local conventions" (immutability and the edits an accepted record takes, superseding part of a record),
  "Template", "Rules" (**A citation changes the outcome**: a precedence over a rule of another record keeps its
  citation; **Numbers freeze**: the cited record, and the record this one adds a requirement to, are linked under
  **Related ADRs**; no check reads the citations of Context)
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
7. **Line planned in ADR-0007.** ADR-0008 links ADR-0007 under **Related ADRs**, and Request 1 says that ADR-0007 gains
   a line under **Related ADRs** for ADR-0008 once ADR-0008 is accepted.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-accepted-record opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-accepted-record
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/edits-and-extra-record.md` is an Opus r1 result of an earlier tree with the sentences about ADR-0007 staying
as it is removed from Request 1, another line of ADR-0007 changed in Request 2, and a record 0009 added there; it fails
checks 3, 4, and 5. `controls/guide-rewritten.md` is an Opus r1 result of an earlier tree with a `README.md` added to
Request 1; it fails the guide check. Both pass check 7, which both baselines fail.

## Results

Runs of 2026-11-16 on tree `ce37d0b5`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because **Numbers freeze** now lets a record's **Related
ADRs** hold a record that adds a requirement to it, or that it adds a requirement to, and Request 1 adds a requirement
to ADR-0007. It is also the control for **A citation changes the outcome**: the new record has to say how R1 relates to
ADR-0007 R4 and R5, so the citation has to stay. All four results pass all seven checks: Request 1 writes a `Proposed`
ADR-0008 with a `TOKEN_ALG_NONE` rule that names ADR-0007, leaves ADR-0007 as it is, says so, and plans the line that
ADR-0007 gains for ADR-0008 once ADR-0008 is accepted; Request 2 fixes the link and changes no other line; neither
writes a guide. Each writes the precedence over ADR-0007 R4 and R5 into R1, and its line for ADR-0007 under **Related
ADRs** says that ADR-0008 adds a requirement to ADR-0007. Opus r2 lets the reason codes of ADR-0007 win, and Opus r1,
Sonnet r1, and Sonnet r2 let `TOKEN_ALG_NONE` win. Opus r1 and Sonnet r1 also say that the guide maps `docs/adr/` to no
layer, which the input does not state.

Three earlier trees of this change ran the case too and passed checks 1 to 6, and their results are not kept: on
`d8b52781` all four let `TOKEN_ALG_NONE` win, on `b7a46b78` Opus let the reason codes of ADR-0007 win, and on `0b92dea7`
Opus r1 and r2 let the reason codes of ADR-0007 win and Sonnet r1 and r2 `TOKEN_ALG_NONE`. The **Numbers freeze** of
`0b92dea7` left the line for an added requirement out of **Related ADRs**, and all four results there still planned the
line in ADR-0007, as **Immutability** asks, and pass check 7.

On tree `d42618eb`, before this change, the four results passed checks 1 to 6 as well; there all four raised the
precedence as an open point, and Sonnet r1 also made it a rule.

In the round before, on tree `bf6c2035`, Sonnet r2 made the precedence a rule, and Opus r2 and Sonnet r2 said that the
guide puts `docs/adr/` in no layer, which the input does not state. The intermediate trees between `bf6c2035` and
`d42618eb`, `89cbfb4e` to `1db689e3`, ran this case as well and passed, and so did `ba170d99`, an earlier tree of this
change; their results are not kept.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since. Opus passes
checks 1 to 6 without the skill, though it offers to move the rule into ADR-0007 instead, and fails check 7: it asks
whether to add the line to ADR-0007 now, instead of planning it for acceptance. Sonnet fails checks 1, 2, 3, and 7: it
adds the rule to ADR-0007 in place as R6 and writes no new record.
