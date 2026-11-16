---
description: "Trigger for the cross-review skill: run it unasked after a large block of implementation, before final-review, and on a plan written to a file, before implementing it."
applyTo: "**"
---

Run `cross-review` on your own work without being asked, after each large block of implementation and before
`final-review`. A block is large when it changes behavior and either spans more than one file or adds or changes more
than about 50 lines of code and tests. A typo, a rename, a version bump, a change to comments or docs only, or a
one-file fix under that size gets `final-review` alone.

Start it once the block builds and its tests pass: `--scope uncommitted` for work not yet committed, `--scope
base:<branch>` for a branch, and the task statement in `--task`. Act on its findings, then run `final-review`, so that
`final-review` sees the code the cross-review fixes produced.

A plan for such a block gets its own run before the code is written: `--scope file:<path>`, run from the repository the
plan is about, with the task statement in `--task`. The file may be a plan-mode plan outside the repository, a design
doc, or an ADR. A plan that exists only in the conversation is written to a file first. Implement the plan once its run
converges.
