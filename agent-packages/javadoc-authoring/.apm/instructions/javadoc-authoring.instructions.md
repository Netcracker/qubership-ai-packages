---
description: Trigger for the javadoc-authoring skill — write, rewrite, or review a Javadoc, KDoc, Groovydoc, or Scaladoc comment.
applyTo: "**/*.{java,kt,kts,groovy,scala}"
---

## Skill trigger: `javadoc-authoring`

When the task involves a doc comment — Javadoc, KDoc, Groovydoc, or Scaladoc — apply the
`javadoc-authoring` skill.

Fires on:

- writing a new doc comment, or deciding whether a member needs one at all;
- editing, rewriting, or shortening an existing one;
- reviewing two versions of one, including a machine-generated rewrite.

A one-line comment is in scope.
