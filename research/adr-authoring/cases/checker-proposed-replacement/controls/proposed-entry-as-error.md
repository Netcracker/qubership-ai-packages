## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so a loaded key set stays in use until the process restarts and no token reloads it after 5 minutes. |
| ADR-0010 R9 | Deferred | The `Defers` trailer names it, with #301, an open issue, as the target. The change leaves the startup case as it was: the key set of a key source is still loaded on the first token that needs it, not at startup. |

Rules not touched: 0.

Other findings:

- Would violate ADR-0020 R3: a loaded key set never expires after the change, so no token reloads it after 1 minute.
- The `Defers` entry `ADR-0020 R3 to #300` names a rule of a `Proposed` record. It produces no verdict, and it is not a trailer error.
- ADR-0010 R9 is unmet in code that this change does not modify. The deferral to #301 covers it.
- There are no trailer errors, no guide errors, and no binding records without numbered rules.

Rule not walked:

- ADR-0020 R3 has no verdict in the table because ADR-0020 is `Proposed` and does not bind the change. Until ADR-0020 is accepted, ADR-0010 R7 is the binding rule. ADR-0010 does not yet list R7 as replaced under **Related ADRs**, so R7 was walked.

Trailer errors:

- `Defers: ADR-0020 R3 to #300` names a rule of a `Proposed` record, which binds nothing.
