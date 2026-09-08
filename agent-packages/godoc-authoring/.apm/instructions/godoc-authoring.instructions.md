---
description: "Trigger for the godoc-authoring skill: load it before writing, editing, or reviewing a doc comment or inline comment in Go."
applyTo: "**/*.go"
---

Before writing, editing, or reviewing a doc comment or inline comment in a `*.go` file, load `godoc-authoring`, and
`english-developer-style` with it. Inside a coding task ("fix the bug", "add the handler") load it as soon as the change
touches a comment, before writing it; a one-line comment, a `//go:` or `//nolint` line, and a CRD field description
count.
