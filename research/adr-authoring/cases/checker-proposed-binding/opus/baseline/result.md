## Change A

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Pass | `internal/verify` still refuses a token whose `exp` has passed with HTTP 401 and `TOKEN_EXPIRED`. It compares `exp` before it reads `kid`, so an expired token with no `kid` also gets `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Fail | A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`. A token whose `kid` names no loaded key still gets `TOKEN_INVALID` instead of `TOKEN_KID_UNKNOWN`. |

- The `Implements: ADR-0007 R5` trailer is wrong. The change implements only the missing-`kid` half of R5. Either the unknown-`kid` branch must return `TOKEN_KID_UNKNOWN`, or the trailer must defer the rest of R5.
- ADR-0007 binds this change even though its status is `Proposed`, because `docs/adr/README.md` says `Proposed` and `Accepted` records bind a change in this repository.

## Change B

| Rule | Verdict | Reason |
| --- | --- | --- |
| ADR-0007 R4 | Pass | `internal/verify` still refuses a token whose `exp` has passed with HTTP 401 and `TOKEN_EXPIRED`. It compares `exp` before it reads `kid`, so an expired token with no `kid` also gets `TOKEN_EXPIRED`. |
| ADR-0007 R5 | Deferred to #12 | A token with no `kid` now gets HTTP 401 and `TOKEN_KID_MISSING`. The unknown-`kid` case still gets `TOKEN_INVALID`, and issue #12 is open and tracks the rest of R5. |

- Issue #12 tracks the unknown-`kid` case, which should return HTTP 401 and `TOKEN_KID_UNKNOWN`. R5 is not complete until #12 is closed.
- ADR-0007 binds this change even though its status is `Proposed`, because `docs/adr/README.md` says `Proposed` and `Accepted` records bind a change in this repository.
