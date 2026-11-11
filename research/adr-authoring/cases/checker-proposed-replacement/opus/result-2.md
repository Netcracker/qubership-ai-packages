## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | After the change, a loaded key set stays in use until the process restarts, and no token reloads it after 5 minutes. |
| ADR-0010 R9 | Deferred | `Defers` names this rule with #301, an open issue. The change leaves loading where it was, on the first token, so the rule is still unmet. |

**Not touched:** 0 rules.

**Other findings:**

- ADR-0020 R3 would be violated. Read as if it bound the change, it fails: a loaded key set is never reloaded, so it is not reloaded after 1 minute either.
- The `Defers` entry for ADR-0020 R3 to #300 gives no verdict. ADR-0020 is `Proposed`, and the guide makes only `Accepted` records bind a change. This entry is not a trailer error.
- No trailer errors were found. #301 is an open issue, and ADR-0010 R9 is a rule of a binding record.
- No guide errors were found. The change touches only `internal/keys/`, which the guide maps to the `keys` layer.

**Rules not walked:**

- ADR-0020 R3 has no verdict because its record is `Proposed` and binds nothing. ADR-0010 R7 still governs the change. ADR-0010 does not list R7 as replaced, and that line is added only when ADR-0020 is accepted.
