## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so a loaded key set stays in use until restart and no token reloads it after 5 minutes. |
| ADR-0010 R9 | Deferred | The change names it under `Defers` to #301 and does not touch it. The key sets still load on the first token that needs them, not at startup, so the rule stays unmet. |

Named apart from the verdicts:

- would violate ADR-0020 R3. The record is `Proposed` and binds nothing. It replaces ADR-0010 R7, `keys` is a layer the change touches, and the trailers name it. Read as binding, it requires a reload after 1 minute, and the change never reloads, so it fails under every reading. The rule gets no verdict. The `Defers` entry for it counts for no verdict and is not a trailer error, and #300 is an open issue.
- Trailer errors: none. Both `Defers` targets, #300 and #301, are open issues.
- Guide errors: none. The change touches only `internal/keys`, which the guide maps to `keys`.
- The change carries no `Implements` trailer. That is allowed, because it claims no rule.

Rules not walked:

- ADR-0020 R3: its record is `Proposed`, so it does not bind the change, and it is read only as described above. ADR-0010 R7 is still walked, because ADR-0010 does not yet name R7 as replaced under **Related ADRs**. That line is added when ADR-0020 is accepted.
- Not touched: none. ADR-0010 has only R7 and R9, and both are walked.
