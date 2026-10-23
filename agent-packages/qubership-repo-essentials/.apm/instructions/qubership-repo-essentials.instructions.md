---
description: Repository-wide conventions for commit messages and tool versions.
applyTo: "**"
---

## Commit messages

Write all commit messages in Conventional Commits format.

Always end commit messages, including drafts, with `Assisted-by: <tool> (<model-id>)`, never `Co-Authored-By:`.
Keep existing trailers and add yours when amending someone else's commit.

## Tool versions

Commands that the docs tell a user to run, in a README, a contributing guide, or a script they invoke, must work on the
oldest tool version the project supports, or on a release a year old where it names none. For a newer flag or behavior,
use a fallback or feature detection rather than raising the requirement. Commands run inside a container image are
exempt.
