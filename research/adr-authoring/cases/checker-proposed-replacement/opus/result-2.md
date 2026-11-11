## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change removes the expiry, so a loaded key set stays in use past 5 minutes and no token reloads it. The trailers do not defer this rule. |
| ADR-0010 R9 | Deferred | The change leaves key sets loading on the first token that needs them, as before, so it does not touch this rule. The rule is still unmet, and `Defers` names it to #301. |

Not touched: 0 rules.

Also in the report:

- **would violate ADR-0020 R3**: ADR-0020 is `Proposed`, so this rule binds nothing, but it is in the `keys` layer and the trailers name it. Read as binding, the change fails it under every reading, because a loaded key set never reloads after 1 minute or at any later time. It gets no verdict.
- **Trailers**: the `Defers` entry for ADR-0020 R3 to #300 names a rule of a `Proposed` record. It counts for no verdict and is not a trailer error. It does not defer ADR-0010 R7, because ADR-0020 does not bind yet and ADR-0010 still governs that rule. The ADR-0010 R9 entry points at #301, which is an open issue, so it is valid. The trailers have no errors.
- **Guide**: the change touches only `internal/keys/`, which the guide maps to `keys`, so there are no guide errors.

Rules not walked:

- **ADR-0020 R3**: its record is `Proposed`, and the guide makes only `Accepted` records bind a change. Step 4 reads it in the `would violate` line, but it gets no verdict.
