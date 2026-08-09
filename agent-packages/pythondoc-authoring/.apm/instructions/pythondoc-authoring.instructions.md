---
description: Trigger for the pythondoc-authoring skill — write, rewrite, or review a docstring or an inline comment in Python source.
applyTo: "**/*.{py,pyi}"
---

## Skill trigger: `pythondoc-authoring`

When the task involves a comment in `*.py` or `*.pyi` — a docstring on a module, class, or
function, or an inline `#` comment — apply the `pythondoc-authoring` skill.

Fires on:

- writing a new docstring, or deciding whether an object needs one at all;
- editing, rewriting, or shortening an existing one;
- reviewing two versions of one, including a machine-generated rewrite;
- editing a docstring that ships as `--help` text or as an OpenAPI description.
