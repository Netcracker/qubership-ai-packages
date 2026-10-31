---
description: Tool versions that commands in user-facing documentation may rely on.
applyTo: "**"
---

## Tool versions

Commands that the docs tell a user to run, in a README, a contributing guide, or a script they invoke, must work on the
oldest tool version the project supports, or on a release a year old where it names none. For a newer flag or behavior,
use a fallback or feature detection rather than raising the requirement. Commands run inside a container image are
exempt.
