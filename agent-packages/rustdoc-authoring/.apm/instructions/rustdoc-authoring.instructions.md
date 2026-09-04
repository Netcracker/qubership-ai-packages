---
description: "Trigger for the rustdoc-authoring skill: load it before writing, editing, or reviewing a doc comment or inline comment in Rust."
applyTo: "**/*.rs"
---

Before writing, editing, or reviewing a doc comment or inline comment in a `*.rs` file, load `rustdoc-authoring`, and
`english-developer-style` with it. Inside a coding task ("fix the bug", "add the method") load it as soon as the change
touches a comment, before writing it; a one-line comment, a `// SAFETY:` comment, and a doc example that the build runs
count.
