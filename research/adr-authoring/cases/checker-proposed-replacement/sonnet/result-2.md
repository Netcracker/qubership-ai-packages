## Change

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0010 R7 | Violates | A loaded key set no longer expires, so no token reloads it after 5 minutes, and R7 requires that reload. |
| ADR-0010 R9 | Deferred | The change names it under `Defers` to #301 and leaves the first-token load as it was, so it still does not load at startup. |

- **Would violate:** `would violate ADR-0020 R3`. ADR-0020 is `Proposed` and binds nothing, and the change touches `internal/keys`, the layer of R3. A key set that never expires fails R3's 1-minute reload under every reading, and no open point lists an answer. R3 gets no verdict and no table row.
- **Trailer errors:** none.
  - The `Defers` entry for ADR-0020 R3 names a rule of a `Proposed` record, so it counts for no verdict and is not an error.
  - It does not defer ADR-0010 R7. ADR-0010 does not name R7 as replaced under **Related ADRs**, so R7 binds the change until ADR-0020 is accepted.
  - #300 and #301 are open issues.
- **Not touched:** 0 rules.
- **Guide errors:** none. Every changed file is under `internal/keys/`, which maps to the layer `keys`.
- **Unchecked records:** none.
- **Rules not walked:** ADR-0020 R3 has no verdict because its record does not bind the change. It is covered by the `would violate` line above.
