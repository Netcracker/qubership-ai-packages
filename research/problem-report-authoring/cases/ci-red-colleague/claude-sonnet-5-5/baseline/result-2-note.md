# Hand-over note for the Slack message to Dana

The draft is `draft.md`, a Slack direct message in Slack markup (backticks and a triple-backtick block). Nothing was sent.

Before you send:

- **The facts are a day old.** Your notes are from 2026-10-30 14:10 UTC, and today is 2026-10-31. Check that `main` is still red at `4f2a9c1`, that no one has already fixed forward or reverted, and that #1311 and #1314 are still blocked. Update or drop the message if any of that changed.
- **The cause is your unchecked guess.** The draft marks it as one. I had no checkout, so I did not read `OrderExporter.export` or `OrderExportTest.java:57`. If you open the code before sending, you could replace the guess with what you find.
- **Nothing was re-run.** The CI results (runs 88407, 88412, 88415, 88419) and the local pass and fail come from your notes. The draft states them as yours ("Locally, ...") and links the runs, and I added no steps of my own.
- **The 40-line trace is trimmed** to the failing test line and the assertion. The rest is JUnit internals per your notes. Run 88412 has the full trace.
- **Left out on purpose:** a deadline or a preferred option. Your notes give neither. If you want a revert by a certain time, or you can revert yourself if Dana is away, add that line.
- **No pronouns for Dana.** Your notes don't say which to use, so the draft addresses Dana directly.
