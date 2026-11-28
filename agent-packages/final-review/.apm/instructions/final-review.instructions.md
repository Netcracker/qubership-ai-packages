---
description: "Trigger for the final-review skill: run it in a fresh subagent when a change is written and before the commit is final, where it adds or changes code, a rule, a command, or a claim someone acts on beyond wording, formatting, or a version number."
applyTo: "**"
---

When a coding task has its code, tests, and comments written and the commit is about to be final, run `final-review` in
a fresh subagent over the change and hand it the task statement. Where the change goes into an open pull request or
merge request, also hand over its title and description, as they stand or as you drafted them anew, and the merge base
of the tip of the branch it merges into and the commit you will push, which is where its diff will start. Hand them over
in whatever form you have them: the text, a link, or a file. Act on the review's substantive findings before committing.
A change with no code counts where it adds or changes a rule, a command, or a claim someone acts on, as in a skill, an
`AGENTS.md` or `CLAUDE.md`, a docs page, or a configuration. A change that only fixes wording, formatting, or a version
number does not count, whether or not it touches code. Do not run it in the same context that wrote the change; the pass
exists because the writer cannot see what it left out.
