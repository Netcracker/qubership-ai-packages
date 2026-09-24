# Editing the problem-report-authoring package

These are instructions for changing the skill under `.apm/skills/problem-report-authoring/`, not for using it to write
a report.

The skill serves several genres, and a rule that helps one can break another: a bug report, a feature or change
request, a question about whether a behavior is intended, a vendor support ticket, a comment on an existing report, an
issue in a team's own backlog, and a short message to a colleague. The first draft of version 1.1.0 was written from
one hardening report, and a review found four of its rules broke other genres: a fix shape demanded of every expected
block, a deletion test that served only the maintainer, a one-line limit on logs of runs that succeeded, and local
consistency ranked with the project's own specification. Only three genres have a case so far (a bug report, a
feature request, and a vendor ticket); check a rule against the other four by reading.

## What an edit owes

- **A rule drawn from one case is stated with the condition under which it holds.** Name the genre, the reader, or the
  evidence it applies to. Where the rule has to hold everywhere, check it against every genre above before writing it.
- **A rule moves in all of its places in the same change.** A rule can sit in the section body, in the §9 table, in the
  §11 checklist, in a reference file, and in the package `README.md`. Search for the rule's own words and its section
  number across all of them before editing.

The cases are under `research/problem-report-authoring/cases/`, and the procedure for running them is in
`agent-packages/AGENTS.md`, under "Testing a skill against its cases". The prompt that runs a case is in
`research/problem-report-authoring/cases/nested-workflow-tag/README.md`.
