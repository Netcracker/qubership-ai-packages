## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so a loaded key set stays in use past 5 minutes and no token reloads it. |
| ADR-0010 R9 | Deferred | The change names this rule under `Defers` with #301, an open issue. Key sets still load on the first token rather than at startup. The change leaves that outcome as it was, so it does not touch the rule. |

Not touched: 0 rules.

Also in the report:

- would violate ADR-0020 R3. If this rule bound the change, a loaded key set would have to be reloaded after 1 minute. After the change, a loaded key set never expires and no token reloads it.
- The trailer entry `ADR-0020 R3 to #300` names a rule of a `Proposed` record. That rule binds nothing, so the entry counts toward no verdict. It is not a trailer error.
- The change carries no `Implements` trailer.
- No guide errors and no unchecked records: the change touches only `internal/keys/`, which the guide maps to the `keys` layer.

Rules not walked:

- ADR-0020 R3 has no verdict. ADR-0020 is `Proposed`, and the reading guide says only `Accepted` records bind a change. Step 4 reads it as if it bound the change, which gives the "would violate" line above.
