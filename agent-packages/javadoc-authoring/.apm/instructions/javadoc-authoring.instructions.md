---
description: "Trigger for the javadoc-authoring skill: load it before writing, editing, or reviewing a doc comment or inline comment in Java, Kotlin, Groovy, or Scala."
applyTo: "**/*.{java,kt,kts,groovy,scala}"
---

Before writing, editing, or reviewing a doc comment or inline comment in a `*.java`, `*.kt`, `*.kts`, `*.groovy`, or
`*.scala` file, load `javadoc-authoring`, and `english-developer-style` with it. Inside a coding task ("fix the bug",
"add the method") load it as soon as the change touches a comment, before writing it; a one-line comment counts.
