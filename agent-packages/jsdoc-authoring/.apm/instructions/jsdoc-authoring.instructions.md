---
description: Trigger for the jsdoc-authoring skill — write, rewrite, or review a JSDoc, TSDoc, or inline comment in JavaScript or TypeScript.
applyTo: "**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"
---

## Skill trigger: `jsdoc-authoring`

When the task involves a comment in JavaScript or TypeScript — a JSDoc or TSDoc block on a
declaration, or an inline `//` comment — apply the `jsdoc-authoring` skill.

Fires on:

- writing a new comment, or deciding whether a declaration needs one at all;
- editing, rewriting, or shortening an existing one;
- reviewing two versions of one, including a machine-generated rewrite;
- editing a type tag in a `.js` file the project type-checks, which is a code change.

A one-line comment is in scope.
