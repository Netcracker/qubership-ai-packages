# Task

Check two pull requests against the repository's architecture decision records. They change the same code and differ
only in their trailers. Check each one on its own, as if the other did not exist.

For each pull request, give a heading `## Change A` or `## Change B`, then a Markdown table with one row per rule that
your check walks: the rule as `ADR-NNNN Rn`, its verdict, and one line of reason. After the table, list anything the
report names apart from the verdicts.

The facts below were checked against the code; treat every fact in them as verified, and add none that they do not
carry.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- `docs/adr/` holds the records. `docs/adr/README.md` is the reading guide: it maps the layer `verify` to
  `internal/verify/`, lists `docs/adr/` and `.github/` as belonging to no layer, and says that `Accepted` records bind a
  change. Issue #12 is open and tracks the rest of ADR-0007 R5.
- `internal/verify` is the code that checks a token. Nothing else in the repository decides the outcome of the cases
  below. Before and after the change, it compares `exp` with the time of the check before it reads `kid`.

## The records

### ADR-0007: Verify every token in `Authorization` before policy evaluation

Status: Accepted. Date: 2026-10-02.

Terms:

- **token**: the value after `Bearer ` in the `Authorization` header of a request.

Rules:

- **R4** (`verify`). A token whose `exp` is earlier than the time of the check is refused with HTTP 401 and the reason
  code `TOKEN_EXPIRED`.
- **R5** (`verify`). A token whose `exp` has not passed is refused with HTTP 401 and the reason code
  `TOKEN_KID_MISSING` when its header has no `kid`, and with HTTP 401 and the reason code `TOKEN_KID_UNKNOWN` when its
  `kid` names no loaded key.

Open points: none.

## The change

Before the change, `internal/verify` refuses both a token with no `kid` and a token whose `kid` names no loaded key
with HTTP 401 and the reason code `TOKEN_INVALID`. It refuses a token whose `exp` has passed with HTTP 401 and
`TOKEN_EXPIRED`, and the change keeps that.

The change adds a branch to `internal/verify`: a token whose header has no `kid` is now refused with HTTP 401 and
`TOKEN_KID_MISSING`. A token whose `kid` names no loaded key still gets HTTP 401 and `TOKEN_INVALID`. Nothing else
changes.

Change A ends its commit message and its description with:

```text
Implements: ADR-0007 R5
```

Change B ends its commit message and its description with:

```text
Defers: ADR-0007 R5 to #12
```
