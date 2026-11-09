## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry of a loaded key set, so the first token after 5 minutes uses the old key set and triggers no reload. |
| ADR-0010 R9 | Deferred | The change names it under `Defers` to #301, and it leaves the first load on the first token that needs the key set, not at startup, so the rule stays unmet. |

Named apart from the verdicts:

- **Trailer error:** the `Defers` entry `ADR-0020 R3 to #300` counts for nothing. ADR-0020 is `Proposed`, and R3 replaces ADR-0010 R7, so R3 binds nothing until ADR-0020 is accepted. ADR-0010 R7 governs until then, and the change is judged against it.
- **Trailer check:** #300 and #301 are open issues. The `ADR-0010 R9 to #301` entry is valid.
- **Missing trailer:** the change has no `Implements` trailer. It claims no rule, and R7 is violated, not implemented.
- **Guide error:** `docs/adr/` has no `README.md`, so no reading guide maps layers to paths. I took the mapping of `internal/keys` to the `keys` layer from the repository facts.
- **Rule not walked:** ADR-0020 R3. It is a rule of a `Proposed` record that replaces ADR-0010 R7, so the walk skips it.
- **Not touched:** no other rule of ADR-0010 or ADR-0020 exists.
