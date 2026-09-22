---
description: "Trigger for the telemetry-authoring skill: load it before writing, changing, or reviewing a log call, a metric, or a span, and when a new branch fails, retries, falls back, or clamps a value."
applyTo: "**"
---

Load `telemetry-authoring` before writing or changing a call to a logger, a metric, or a span, and before deciding
what a new failure, retry, fallback, clamped value, or waited-on state should emit. A coding task reaches this point
the moment the branch is written, not when the pull request is due: load it then, and read its `references/` file for
the repository's ecosystem before the first call. Also load it to review instrumentation in a diff, including
instrumentation that is conspicuously absent. Wording, tense, sentence length, and dialect of the message belong to
the developer-style skill of the language it is written in (`english-developer-style` for English); load that too.
