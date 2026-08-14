# Report format (all axes)

Write one Markdown file to the path given in your instructions. Also return the structured findings the schema asks
for — the two must agree; the Markdown is for humans, the structured payload is for the pipeline.

Report language: Russian, with identifiers, paths, and technical terms left in English. Structure:

## Summary

At most ten lines. What you attacked, what you found, and the one thing the reader should act on first. No preamble,
no restatement of the task.

## Findings

Ordered by proposed severity, then by how firmly you established each one. One block each:

```markdown
### <AXIS>-01 <one-line claim, stated as a defect> — HIGH

- **Where:** `path/to/file.go:123-141`
- **Trigger:** what has to happen — inputs, ordering, scale, or failure mode
- **Actual:** what the code does today under that trigger
- **Expected:** what it should do, and where that is established — spec section, doc comment, type signature, a
  sibling that gets it right, or a named convention. No source for the expectation means no defect
- **Consequence:** the observable damage, in the terms of whoever gets hurt
- **Проверка:** `executed` / `traced` / `inferred`, plus the artifact — for `executed`, the command and the decisive
  line of its output; for `traced`, the branches you followed; for `inferred`, the assumption you did not check
- **Falsified:** what you checked that could have made this safe, and why it does not
- **Tool limit:** only for a finding in an artifact written on a technology from the profile's inventory: the
  documented limit of that technology that makes the defect possible, or `none`
- **Fix:** the minimal change, or the design change with its trade-off
```

The heading carries your **proposed** severity and nothing else. **Do not write a confidence label**: the verifier
appends `— CONFIRMED` or `— PLAUSIBLE` after checking the finding, and it may only write `CONFIRMED` if it executed
something itself. Severity travels the same way — the verifier may lower it, and the consolidator settles it, being
the only stage that sees every axis. A finding that arrives pre-labelled tells the next reader what to conclude,
which is exactly what these splits are meant to prevent.

Use the axis key as the finding prefix: `CONC-01`, `SEC-03`, `ARCH-02`.

## Отклонено автором

The candidates you considered and did not report, one line each: the defect you suspected, the file, and the specific
mechanism that made it a non-issue — the guard, the caller that never passes that value, the test that already pins
it, the spec that permits it. Mandatory, and it may well be longer than the findings list.

This is not padding. It is the record of the half of the review that kept the report short, it is where the verifier
looks for something you dismissed too fast, and it is the only way a reader can tell a clean subsystem from a shallow
pass over a dirty one.

## Checked and sound

The checks you **ran** that did not reveal a defect, one line each, each naming what you executed — the test, the
command, the scanner, the fuzz session and its iteration count. Not "I read the connection package and it looked
fine": that belongs in `coverage`, not here. This section is mandatory, and an axis that reports only defects gives
the next reviewer no information about what is already covered.

## Cross-axis notes

One line per thing you noticed that belongs to a different axis. No development, no evidence — just a pointer.

## Open questions

Anything the repository could not settle, phrased so a maintainer can answer in one sentence, each annotated with
which finding it would resolve.

Then mark **at most one** of them as the question for the user, and only when the answer would materially change your
conclusions — a different severity, a finding that appears or disappears. Everything else is a note for the
maintainers. A list of twelve equally-weighted questions gets read as none: choosing the one that matters is part of
the work, not a formality.

## What not to include

No plan, no next steps, no offer to implement anything, no summary of the codebase for its own sake, no restating of
these instructions. The report is the deliverable.
