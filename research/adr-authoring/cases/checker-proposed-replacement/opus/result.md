## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so a loaded key set stays in use past 5 minutes and no token reloads it. |
| ADR-0010 R9 | Deferred | `Defers` names it to #301, an open issue. The change leaves the first load on the first token that needs the key set, so key sets still don't load at startup. |

Not touched: 0 rules.

The two rows have different root causes. ADR-0010 R7 fails because this change deletes the expiry. ADR-0010 R9 was already unmet before the change, because key sets loaded on the first token and not at startup, and this change leaves that unchanged.

Named apart from the verdicts:

- would violate ADR-0020 R3. The change never reloads a loaded key set, so no key set is reloaded after 1 minute. This has the same root cause as the ADR-0010 R7 row.
- The `Defers` entry `ADR-0020 R3 to #300` names a rule of a `Proposed` record. It counts for no verdict and is not a trailer error. It doesn't defer ADR-0010 R7, which binds the change and which the change touches.
- Trailer errors: none. Guide errors: none. The change touches only `internal/keys/`, which the guide maps to `keys`.
- Unchecked records: none.

Rules not walked:

- ADR-0020 R3 got no verdict because ADR-0020 is `Proposed`, and the guide makes only `Accepted` records bind a change. Even after acceptance, the rule replaces ADR-0010 R7, and ADR-0010 R7 governs until then. It is read only for the "would violate" line above.
