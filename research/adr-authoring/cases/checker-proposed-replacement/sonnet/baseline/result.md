## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violated | The change deletes the 5-minute expiry, so a loaded key set stays in use until restart and no token reloads it. |
| ADR-0010 R9 | Not met before the change, unchanged by it; deferred to #301 | `internal/keys` loaded each key set on the first token before the change and still does, so the change does not move it. |
| ADR-0020 R3 | Not binding; deferred to #300 | The record is Proposed, so its 1-minute rule is not in force. The change also fails it, because the key set never reloads. |

ADR-0010 R7 stays in force because ADR-0020, the record that replaces it, is only Proposed. The change's trailer defers neither R7 nor the loss of reloading, so this violation is not covered by a deferral.

**Named in the report apart from the verdicts**

- Issue #300 and issue #301 are open. The trailer `Defers: ADR-0020 R3 to #300; ADR-0010 R9 to #301` points at both.
- The deferral to #301 covers R9 only. It does not excuse the R7 violation.
- The deferral to #300 covers ADR-0020 R3, a Proposed rule that does not bind today.

**Rules not walked**

None. ADR-0010 and ADR-0020 list only R7, R9, and R3, and the check walked all three. `docs/adr/` has no `README.md`, so there is no index of further records.
