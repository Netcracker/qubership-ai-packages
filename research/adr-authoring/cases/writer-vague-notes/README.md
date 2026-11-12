# Case: meeting notes with an open value, in a repository without records

The input is meeting notes that leave the retry count open ("a few times"), give the timeout (5 seconds), and leave the
owner unsettled, for a repository with no records. The skill asks for a visible placeholder and an open point for the
retry count, no invented value or account, a question whether to add the reading guide that names the trailers it
commits the team to, with no guide added before the answer, and a `Proposed` status. The 5-second timeout is the noise
input for the placeholder rule: a value the notes give stays.

## Skill parts

- `SKILL.md`: "Local conventions" (location, status), "Template", "Open points" (a value the input leaves open),
  "The reading guide" (asked about before it is added), "Drafting from the user's input"
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0001.** A record file `docs/adr/0001-<slug>.md`.
2. **Guide not added.** No `README.md` beside the record and no change to `AGENTS.md`: the user has not agreed to the
   guide yet.
3. **Retry placeholder.** A rule line that mentions the retries carries a placeholder in angle brackets, and no rule
   line puts a number next to a retry or an attempt.
4. **Open point for the retries.** The record's **Open points** asks for the retry count.
5. **Timeout kept.** The record states the 5-second timeout and has no placeholder for it.
6. **Owner not invented.** The **Owner** section holds a placeholder, "TBD", or "not assigned", names no account, and
   the message asks the user for an owner.
7. **Guide asked about.** The message asks whether to add the reading guide, and the question names the trailers it
   would commit the team to.
8. **Proposed.** The record's status is `Proposed`.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-vague-notes opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-vague-notes
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/invented-values.md` is `opus/result.md` as run on tree `61999f9e`, with the record renamed to 0002, the
timeout replaced by `<timeout>`, and the owner set to `@platform-lead`; it fails checks 1, 5, and 6, and checks 2 and 7,
since the skill at `61999f9e` added the guide unasked. `controls/three-retries.md` is `sonnet/result.md` as run on the
same tree, with `3` in place of `<retry count>`; it fails check 3, and checks 2 and 7 for the same reason.

## Results

Runs of 2026-11-11 on tree `d42618eb`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. The case ran again on this tree because "What belongs in an ADR" now sorts each
requirement into a decision, a defect, or a guarantee of a dependency, "Open points" gives a question about a defect no
open point, and "Drafting from the user's input" says how such a question is answered. Every requirement of the notes is
a decision, so the new passages have to stay quiet. All four results pass all eight checks by meaning. Each writes
`docs/adr/0001-<slug>.md` with a `<retry count>` placeholder in the retry rules and an open point that asks for it,
keeps the 5-second timeout, leaves the owner as a placeholder and asks for one, and sets `Proposed`. None adds a guide
or changes `AGENTS.md`, and each asks whether to add `docs/adr/README.md`, naming the `Implements:` and `Defers:`
trailers it would commit the team to. No result names a defect or proposes an issue. `check.py` fails check 7 for Sonnet
r1 on the marker: its question, "Do you want me to add it, with that commitment?", comes two sentences after the
trailers, past the window the check reads.

The previous round, on tree `bf6c2035`, passed all eight checks too. The intermediate trees of this change, `89cbfb4e`
to `1db689e3`, ran this case as well and passed by meaning; their results are not kept.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since, and the current
checks grade them. Both keep the retry count as "TBD" with no rule, keep the owner as "TBD", and ask for both: by
meaning that passes checks 3 and 6, though not by marker. Sonnet lists the retries under "Open items", which passes
check 4 by meaning, and Opus has no open point for them. Both fail checks 7 and 8: no word about a guide, and `Accepted`
as the status.

Tree `b7a46b78` changes only "Rules": **Numbers freeze** asks for a link under **Related ADRs** to every cited record;
**One home** says when a rule cites another rule, that a citation of a rule of another record names what that rule is
about and none of what it decides, that a rule other rules imply is left out, and that a case a rule of another record
leaves unclear belongs to that record, and it takes in **No pointer rules**; **Every requirement is a rule** asks for a
rule number instead of a record. This case writes records, but its skill parts list no part of "Rules", and its inputs
hold no rule of another record, so the results above stand for the tree.
