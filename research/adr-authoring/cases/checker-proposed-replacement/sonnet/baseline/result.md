## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violated | The change deletes the 5-minute expiry, so a loaded key set stays in use until restart and no token reloads it. |
| ADR-0010 R9 | Violated | The first load still happens on the first token that needs a key set, not at startup before the first request. The change leaves this behavior as it was. |

- **Trailer `Defers: ADR-0020 R3 to #300; ADR-0010 R9 to #301`:** The README and the records give no way to waive an Accepted rule by deferring it, so the trailer leaves both verdicts unchanged.
  - The `ADR-0010 R9` deferral names a rule that binds. The change leaves its violation as it was.
  - The `ADR-0020 R3` deferral names a rule that does not bind (see below). It also does not cover `ADR-0010 R7`, the rule the change actually breaks.
- **Issues #300 and #301:** Both are open. Neither changes a verdict.
- **ADR-0020 R3 (not walked):** `ADR-0020` is Proposed, and the README says only Accepted records bind a change. Its claim to replace `ADR-0010 R7` has no effect yet, so R7 still binds. The change also does not implement R3, because it removes the expiry instead of setting it to 1 minute.
- **Layers:** `internal/keys` is the `keys` layer, so R7 and R9 both apply to the change. `docs/adr/` and `.github/` belong to no layer, and the change touches neither.
