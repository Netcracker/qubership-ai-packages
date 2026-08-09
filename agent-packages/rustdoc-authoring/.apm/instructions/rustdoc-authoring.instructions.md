---
description: Trigger for the rustdoc-authoring skill — write, rewrite, or review a doc comment or an inline comment in Rust source.
applyTo: "**/*.rs"
---

## Skill trigger: `rustdoc-authoring`

When the task involves a comment in `*.rs` — a `///` or `//!` doc comment, an inline `//`
comment, or a `// SAFETY:` comment — apply the `rustdoc-authoring` skill.

Fires on:

- writing a new comment, or deciding whether an item needs one at all;
- editing, rewriting, or shortening an existing one;
- reviewing two versions of one, including a machine-generated rewrite;
- adding or editing a doc example, which the build compiles and runs.
