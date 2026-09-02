---
description: "Trigger for the change-description-authoring skill: write, rewrite, or review a commit message, a pull request title or description, or a changelog entry."
applyTo: "**"
---

## Skill trigger: `change-description-authoring`

When the task involves describing a change (a commit subject or body, a pull request or merge
request title or description, or a changelog or release-note entry), apply the
`change-description-authoring` skill.

Fires on:

- writing one, including the message for a commit the agent is about to make;
- editing, rewriting, or shortening an existing one;
- reviewing one, or comparing two versions of one, including a machine-generated rewrite;
- deciding whether a change needs a changelog entry at all.

A one-line subject is in scope.
