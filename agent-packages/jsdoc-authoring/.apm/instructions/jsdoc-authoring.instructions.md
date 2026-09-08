---
description: "Trigger for the jsdoc-authoring skill: load it before writing, editing, or reviewing a JSDoc or TSDoc block or an inline comment in JavaScript or TypeScript."
applyTo: "**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}"
---

Before writing, editing, or reviewing a JSDoc or TSDoc block or an inline comment in a JavaScript or TypeScript file
(`*.js`, `*.jsx`, `*.mjs`, `*.cjs`, `*.ts`, `*.tsx`, `*.mts`, `*.cts`), load `jsdoc-authoring`, and
`english-developer-style` with it. Inside a coding task ("fix the bug", "add the handler") load it as soon as the change
touches a comment, before writing it; a one-line comment counts, and so does a type tag in a `.js` file the project
type-checks, which is a code change.
