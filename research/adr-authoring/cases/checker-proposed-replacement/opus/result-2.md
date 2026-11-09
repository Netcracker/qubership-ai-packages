## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so a loaded key set stays in use until the process restarts and no token reloads it after 5 minutes. |
| ADR-0010 R9 | Deferred | The change names this rule under `Defers` to #301 and doesn't touch it, and the key set still loads on the first token that needs it rather than at startup. |

`Not touched`: 0 rules.

Reported apart from the verdicts:

- **Trailer error:** `Defers: ADR-0020 R3 to #300` counts for nothing. ADR-0020 is `Proposed`, and R3 replaces the accepted ADR-0010 R7, so R3 binds nothing until ADR-0020 is accepted. Until then ADR-0010 R7 governs, and this entry doesn't defer it. Issue #300 exists and is open, so the target itself is valid.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps `internal/keys` to the `keys` layer. The files the change edits sit under no mapped path. ADR-0010 R7 is walked because the change alters its outcome. ADR-0010 R9 is walked because the change names it under `Defers`. With no guide to override the default, `Accepted` and `Proposed` records both bind.

Rules not walked:

- **ADR-0020 R3:** this rule belongs to a `Proposed` record and replaces the accepted ADR-0010 R7. The walk skips it until ADR-0020 is accepted.
