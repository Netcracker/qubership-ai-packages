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

Runs of 2026-11-11 on tree `bf6c2035`, graded by reading; both models at the default effort. "r1" and "r2" are
`result.md` and `result-2.md`. Trees `6c8380e9`, `7aeb0ec4`, `9fb67955`, and `025f4b62` change only "Checking a change",
its steps 1 and 4 and its paragraph on cases, which this case does not read, so these results stand for them. All four
results pass all eight checks. Each writes `docs/adr/0001-<slug>.md` with a `<retry count>` placeholder in the retry
rules and an open point that asks for it, keeps the 5-second timeout, leaves the owner open and asks for one, and sets
`Proposed`. None adds a guide or changes `AGENTS.md`, and each asks whether to add `docs/adr/README.md`, naming the
`Implements:` and `Defers:` trailers it would commit the team to. Sonnet r2 also makes the owner an open point that
affects no rule, where the skill asks for an owner in the conversation alone. `check.py` passes check 7 for Opus r1 on
the wrong sentence; the question it should quote, "Would you like me to add a guide in `docs/adr/README.md`?", comes two
sentences later.

The baselines ran on 2026-11-09 with `english-developer-style` alone; the prompt has not changed since, and the current
checks grade them. Both keep the retry count as "TBD" with no rule, keep the owner as "TBD", and ask for both: by
meaning that passes checks 3 and 6, though not by marker. Sonnet lists the retries under "Open items", which passes
check 4 by meaning, and Opus has no open point for them. Both fail checks 7 and 8: no word about a guide, and `Accepted`
as the status.

Tree `3b230c74` changes only the bullet on named sets under "Terms" and rule R3 of the example record, so that neither
asks for an approver as a rule. No input of this case has a set that is expected to change, and no result of it writes a
named set, an approval rule, or a `CODEOWNERS` entry, though every session reads the example; the results above stand
for the tree.
