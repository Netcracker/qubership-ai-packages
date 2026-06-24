---
description: Trigger for the adr-authoring skill — write or supersede an Architecture Decision Record under docs/adr.
applyTo: "**/docs/adr/**"
---

## Skill trigger: `adr-authoring`

When the user wants to capture an architecture or system-design decision —
writing a new record under `docs/adr/`, drafting one from notes, or superseding
an existing one — apply the `adr-authoring` skill.

Fires on:

- "write an ADR", "document this decision", "add a decision record";
- a described choice worth tracking (a pattern, non-functional requirement,
  dependency, interface, or tool selection), even when the user does not say "ADR";
- any edit under `docs/adr/`.
