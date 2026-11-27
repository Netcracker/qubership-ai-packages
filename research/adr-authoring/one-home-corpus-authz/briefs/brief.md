# Axis brief (arm {ARM})

You check one Architecture Decision Record for one kind of problem only. Do not report anything else.

Record under check: `{REPO}/docs/decisions/{FILE}` ({ADR}). The checkout `{REPO}` is read-only: do not edit, commit, or
run git commands that write. The other records it relates to are in the same directory: those its Related ADRs section
names, and any other record whose rules decide the same subject. Read the record under check in full, and read the
related records as far as you need.

The rule you check against (from the `adr-authoring` skill; do not load the skill, this text is all of it you need):

> **One home**: a requirement is stated once. Every other mention cites it by number and does not restate its
> conditions, because a restatement drifts. A table that summarizes rules holds rule numbers rather than conditions.

{PROCEDURE}

Report only text of {ADR} that restates a requirement, a constraint, or a consequence owned by another record (or, where
{ADR} owns it, text of another record that restates {ADR}). A citation by number that adds no restated condition is
not a finding. A decision {ADR} makes for itself is not a finding.

Write a JSON array to `{OUT}`, `[]` if nothing is found. Each element:

```json
{"lines": "<file>:<start>-<end>", "quote": "<verbatim text>", "owner": "ADR-NNNN Rn (or section)",
 "owner_quote": "<verbatim text of the owning statement>", "why": "<one sentence>"}
```

Write nothing else anywhere. Reply with the number of findings.
