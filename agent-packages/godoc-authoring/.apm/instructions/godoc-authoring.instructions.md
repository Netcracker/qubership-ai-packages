---
description: Trigger for the godoc-authoring skill — write, rewrite, or review a doc comment or an inline comment in Go source.
applyTo: "**/*.go"
---

## Skill trigger: `godoc-authoring`

When the task involves a comment in `*.go` — a doc comment on a declaration or an inline `//`
comment inside a function — apply the `godoc-authoring` skill.

Fires on:

- writing a new comment, or deciding whether a declaration needs one at all;
- editing, rewriting, or shortening an existing one;
- reviewing two versions of one, including a machine-generated rewrite;
- editing a field comment that ships as a CRD description.
