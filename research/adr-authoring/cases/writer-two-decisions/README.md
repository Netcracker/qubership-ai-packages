# Case: notes with two decisions, and notes with one

The input is two requests. The first has notes with two decisions that different people settle (token verification by
the security architect, a liveness endpoint by the platform team); the skill writes at most one record and proposes the
split. The second has notes with three choices that one authority settles and that change together, which are one
decision and one record. Request 2 is the noise input for the split rule.

## Skill parts

- `SKILL.md`: "What belongs in an ADR" (one decision per record, split no further, propose the split); "Terms" (a named
  set for the trusted key sources, a set that is expected to change; no check reads it)
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **At most one record.** Request 1 writes at most one record file.
2. **Split proposed.** Request 1's message proposes a separate record for the other decision; a sentence that denies a
   split does not count.
3. **One record.** Request 2 writes exactly one record file.
4. **No split.** Request 2's message proposes no split.
5. **No guide written.** Neither request writes a `README.md`: the repository has its guide.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-two-decisions opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-two-decisions
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/split-one-decision.md` is `opus/result.md` with a second record and a proposed split added to Request 2; it
fails checks 3 and 4. `controls/merged-no-split.md` is `opus/result.md` with the message of Request 1 replaced by "Both
choices are in one record, and there is no need to split them."; it fails check 2. `controls/guide-rewritten.md` is
`opus/result.md` with a `README.md` added to Request 1; it fails the guide check.

## Results

Runs of 2026-11-11 on tree `3b230c74`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because its trusted key sources form a set that is
expected to change, which the bullet on named sets under "Terms" covers, and that bullet changed. All four results pass
all five checks: Request 1 writes ADR-0006 for the security architect's decision alone and offers ADR-0007 for the
health endpoint, and Request 2 writes one record for the three choices and proposes no split. Sonnet r2 proposes the
split in a sentence that also says the probe "does not follow from a record about tokens", so `check.py` skips it and
fails check 2 on the marker, while the meaning matches. Three of them define the trusted key sources as a named set,
`trusted-key-sources`, and Sonnet r2 as the sources the service is configured to trust; all four leave the criterion to
an open point, and none writes a rule about who approves a member. No result names an address.

The previous round, on tree `bf6c2035`, passed the same way, and three of its four results added an open point on who
approves a new trusted key source, as the bullet on named sets then asked.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since. Both write two
records for Request 1 without asking ("I split the notes into two ADRs"), which fails check 1 and, by meaning, check 2.
