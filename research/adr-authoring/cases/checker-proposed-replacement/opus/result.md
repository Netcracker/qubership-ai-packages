## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so once a key set is loaded no token reloads it, including the first token that needs it after 5 minutes. |
| ADR-0010 R9 | Deferred | The change leaves the first load on the first token that needs the key set. Startup loading is unmet before and after the change, and the `Defers` trailer names #301, which is an open issue. |

There is one root cause: deleting the expiry of a loaded key set in `internal/keys` breaks ADR-0010 R7. The ADR-0010 R9 deferral comes from the lazy first load, which the change leaves as it is. Not touched: 0 rules.

**Items outside the verdicts**

- **Trailer entry that counts for nothing.** `Defers: ADR-0020 R3 to #300` names a rule of a `Proposed` record that replaces ADR-0010 R7, which is accepted. ADR-0020 R3 binds nothing until ADR-0020 is accepted, so the entry counts for nothing even though #300 exists. ADR-0010 R7 governs this change, and the trailers do not name it.
- **Guide error.** `docs/adr/` has no `README.md`, so no reading guide maps the `keys` layer to any path. The changed code in `internal/keys` therefore sits under no mapped path. The walk could not select rules by layer. It covered the rules the change touches and the rules it names under `Defers`, which are all the ADR-0010 rules listed here.

**Rules not walked**

- **ADR-0020 R3:** This rule belongs to a `Proposed` record and replaces ADR-0010 R7, which is accepted. It binds nothing until ADR-0020 is accepted, so the walk skips it.
