---
description: "Trigger for the pythondoc-authoring skill: load it before writing, editing, or reviewing a docstring or an inline comment in Python."
applyTo: "**/*.{py,pyi}"
---

Before writing, editing, or reviewing a docstring or an inline comment in a `*.py` or `*.pyi` file, load
`pythondoc-authoring`, and `english-developer-style` with it. Inside a coding task ("fix the bug", "add the method")
load it as soon as the change touches a docstring or a comment, before writing it; a one-line comment counts, and so
does a docstring that ships as `--help` text or as an OpenAPI description.
