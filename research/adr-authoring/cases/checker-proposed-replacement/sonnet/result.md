## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change removes the expiry, so a loaded key set stays in use until the process restarts and no token reloads it after 5 minutes. |
| ADR-0010 R9 | Deferred | The change does not alter startup loading, which was already unmet because the first load happens on the first token. `Defers` names #301, an open issue. |

Named apart from the verdicts:

- Trailer error: the `Defers` entry `ADR-0020 R3 to #300` counts for nothing. ADR-0020 is `Proposed` and replaces ADR-0010 R7, so ADR-0020 R3 binds nothing until that record is accepted. ADR-0010 R7 governs until then, which is why it gets `Violates`.
- Rule not walked: ADR-0020 R3, for the reason above. Its verdict is neither `Conforms` nor `Deferred`.
- No `README.md` in `docs/adr/`, so there is no reading guide with a layer map. I took the `keys` layer to be `internal/keys` from the repository facts.
