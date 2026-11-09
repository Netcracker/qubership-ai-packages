# Case: meeting notes with an open value, in a repository without records

The input is meeting notes that leave the retry count open ("a few times"), give the timeout (5 seconds), and leave
the owner unsettled, for a repository with no records. The skill asks for a visible placeholder and an open point for
the retry count, no invented value or account, the reading guide added by this first record with the user told, and a
`Proposed` status. The 5-second timeout is the noise input for the placeholder rule: a value the notes give stays.

## Skill parts

- `SKILL.md`: "Local conventions" (location, status), "Template", "Open points" (a value the input leaves open),
  "The reading guide" (added by the first record, the user told), "Drafting from the user's input"
- `english-developer-style`: runs with the case; no check tests its rules

## Checks

1. **Record 0001.** A record file `docs/adr/0001-<slug>.md`.
2. **Guide added.** A `README.md` beside it.
3. **Retry placeholder.** A rule line that mentions the retries carries a placeholder in angle brackets, and no rule
   line puts a number next to a retry or an attempt.
4. **Open point for the retries.** The record's **Open points** asks for the retry count.
5. **Timeout kept.** The record states the 5-second timeout and has no placeholder for it.
6. **Owner not invented.** The **Owner** section holds a placeholder, "TBD", or "not assigned", names no account, and
   the message asks the user for an owner.
7. **User told about the guide.** The message mentions the `README.md` or the reading guide.
8. **Proposed.** The record's status is `Proposed`.

## Running it

From the repository root:

```bash
research/adr-authoring/cases/run-case.sh research/adr-authoring/cases/writer-vague-notes opus result
python3 research/adr-authoring/cases/check.py research/adr-authoring/cases/writer-vague-notes
```

`check.py` marks every check; a PASS is a marker found, so read the result before recording a grade.

`controls/invented-values.md` is `opus/result.md` with the record renamed to 0002, the timeout replaced by `<timeout>`,
and the owner set to `@platform-lead`; it fails checks 1, 5, and 6. `controls/three-retries.md` is `sonnet/result.md`
with `3` in place of `<retry count>`; it fails check 3.

## Results

Runs of 2026-11-09 on tree `61999f9e` (the skill at a49f24d), graded by reading; both models at the default effort. "r1"
and "r2" are `result.md` and `result-2.md`. All four results pass all eight checks. Each writes
`docs/adr/0001-<slug>.md` with a `<retry count>` placeholder in the retry rule and an open point that asks for it, keeps
the 5-second timeout, leaves the owner as a placeholder ("Not assigned yet.", "TBD", or `<owner>`) and asks for one,
adds `docs/adr/README.md`, tells the user about the guide, and sets `Proposed`.

The baselines ran the same day with `english-developer-style` alone. Both keep the retry count as "TBD" rather than a
number, keep the owner as "TBD", and ask for both: by meaning that passes checks 3 and 6, though not by marker, and
Sonnet also lists the retries under "Open items", which passes check 4 by meaning. Both fail checks 2, 7, and 8: no
guide, no word about one, and `Accepted` as the status.
