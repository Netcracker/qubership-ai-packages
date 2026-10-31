---
description: "Trigger for the final-review skill: run it in a fresh subagent when a change is written and before the commit is final, where it adds or changes code, a rule, a command, or a claim someone acts on."
applyTo: "**"
---

When a coding task has its code, tests, and comments written and the commit is about to be final, run `final-review` in
a fresh subagent over the change, hand it the task statement, and act on its substantive findings before committing. A
change with no code counts where it adds or changes a rule, a command, or a claim someone acts on, as in a skill, an
`AGENTS.md` or `CLAUDE.md`, a docs page, or a configuration; a change that only fixes wording, formatting, or a version
number does not. Do not run it in the same context that wrote the change; the pass exists because the writer cannot see
what it left out.
