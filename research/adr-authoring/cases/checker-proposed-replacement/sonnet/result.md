## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | The change deletes the expiry, so a key set loaded once is never reloaded, where R7 requires a reload on the first token after 5 minutes. |
| ADR-0010 R9 | Deferred | The change leaves the key sets loading on the first token that needs them, not at startup. It names R9 under `Defers` to #301, which is open. |

- **would violate ADR-0020 R3**: ADR-0020 is `Proposed` and binds nothing, so the rule gets no verdict. A key set that is never reloaded fails R3's 1-minute reload under every reading. The `Defers` entry for ADR-0020 R3 counts for no verdict and is not a trailer error.
- **The `Defers` entry for ADR-0020 R3 does not cover the R7 violation.** ADR-0020 does not bind yet, and ADR-0010 R7 governs until it is accepted.
- **Trailer errors**: none. The `Defers` entry for ADR-0010 R9 names a rule of a binding record and an open issue.
- **Guide errors**: none.
- **Not touched**: 0 rules. ADR-0010 has only R7 and R9, and both are walked.
- **Rules not walked**: ADR-0020 R3 is not walked for a verdict because its record is `Proposed`. It appears only in the `would violate` line above.
