---
description: "Trigger for the test-authoring skill: load it before writing, editing, or reviewing a test, and when a coding task ends in one."
applyTo: "**"
---

Before writing, editing, or reviewing a test in any language, load `test-authoring`, and with it the developer-style
skill of the language the repository writes in (`english-developer-style` unless these instructions name another). A
coding task ends in one ("fix the bug", "add the method"): load it when the change is done and before the first test is
written, because the skill decides which tests the change owes, at which level, and how each is shown able to fail.
Before writing the first assertion, read the files under its `references/` that its §0 names for the project's test
engine and assertion library. The comment above a test belongs to the doc-comment skill of its language; load
that one too.
