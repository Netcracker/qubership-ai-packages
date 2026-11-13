## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violated | ADR-0010 is Accepted, so R7 binds. R7 requires a loaded key set to expire after 5 minutes and reload on the next token that needs it. The change deletes that expiry, so a key set now stays in use until the process restarts. |
| ADR-0010 R9 | Violated, pre-existing | Before and after the change, `internal/keys` loads a key set on the first token that needs it, not at startup. The change neither causes this nor fixes it. |

The report also names these points apart from the verdicts:

- **The `Defers:` line doesn't mention ADR-0010 R7.** R7 is the only rule this change breaks. ADR-0020 says it replaces R7, but ADR-0020 is Proposed, and only Accepted records bind a change. R7 still binds at 5 minutes.
- **Deferring ADR-0020 R3 to #300 has nothing to defer.** R3 is in a Proposed record, so it doesn't bind this change. It also wouldn't cover the change if it were Accepted. R3 still expires a key set, after 1 minute, and the change removes expiry entirely.
- **Deferring ADR-0010 R9 to #301 leaves its verdict unchanged.** Issue #301 is open. The facts give a `Defers:` line no effect on a verdict, so R9 is still recorded as violated. The violation predates this change.

One rule was not walked:

- **ADR-0020 R3:** ADR-0020 is Proposed. The reading guide says only Accepted records bind a change.
