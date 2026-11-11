## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry of a loaded key set, so no token reloads it after 5 minutes. The rule requires the first token after that to reload it. |
| ADR-0010 R9 | Deferred | The change names it under `Defers` to #301 and leaves startup unchanged. The key set of each key source is still loaded on the first token that needs it, not at startup, so the rule is unmet. |

Named apart from the verdicts:

- `would violate ADR-0020 R3`. The record is `Proposed`, so the rule binds nothing and gets no verdict. It sits in the `keys` layer, which the change touches, and the trailers name it. Read as binding, it requires a reload after 1 minute, and a key set that never expires fails that under every reading.
- Trailer entries. The `Defers` entry for ADR-0020 R3 names a rule that binds nothing, so it counts for no verdict and is not an error. The `Defers` entry for ADR-0010 R9 is valid, because #301 is an existing issue. The commit message and the description carry no `Implements` trailer, and the change does not defer ADR-0010 R7.
- ADR-0010 R7 is still walked. ADR-0010 has no line under **Related ADRs** that names R7 as replaced. Only ADR-0020, which is `Proposed`, says it replaces R7, so R7 governs the change.

Rules not walked:

- ADR-0020 R3 is not walked in step 2, because the record does not bind the change. The `would violate` line above covers it.
- No other rule of a binding record exists. No rule is `Not touched`, so the count is 0.
