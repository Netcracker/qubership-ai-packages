# Hand-over note: Slack DM to Dana about the red `main`

Nothing was sent. `draft.md` is the message body, written as a single Slack direct message, and Slack renders its backticks and the `text` block.

## What the message rests on

Everything in it comes from your notes taken on 2026-10-30 at 14:10 UTC. I ran nothing and could not open CI. The message presents the local run as yours ("Locally, ... fails"), which matches your notes.

## Before you send

- **The guess about `OrderExporter.export`.** It is marked as unchecked in the message. If you want it checked first, read the `4f2a9c1` diff of `OrderExporter.export` and look at what `OrderExportTest.java:57` asserts.
- **Links to the re-runs.** The message names runs 88415, 88419, and 88407 by number only. Your notes give a URL for 88412 alone, so I did not build the other URLs. If Dana's CI search does not find runs by number, paste their links.
- **State of `main` since 14:10 UTC.** If anything has merged since then, or Dana has already reacted, check run 88419 or a newer one before you send.
- **Whom to ask.** Your notes name Dana as the commit author. If someone else merged it, or the team has a build-cop rotation, they may also need the question.

## What I left out on purpose

- The trace beyond the three lines. The run link has the rest, and the remaining 37 lines are JUnit internals.
- JDK 21.0.5, Gradle 8.10.2, and macOS 15.1. CI fails the same way, so the local versions don't affect the outcome.
- The merge time (11:42 UTC). The commit hash already pins the start of the failure.
