# Task

Check two pull requests against the repository's architecture decision records. Check each one on its own, as if the
other did not exist.

For each pull request, give a heading `## Change A` or `## Change B`, then a Markdown table with one row per rule that
your check walks: the rule as `ADR-NNNN Rn`, its verdict, and one line of reason. After the table, list anything the
report names apart from the verdicts.

The facts below were checked against the code; treat every fact in them as verified, and add none that they do not
carry.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- `docs/adr/` holds the records. `docs/adr/README.md` is the reading guide: it maps the layer `verify` to
  `internal/verify/`, lists `docs/adr/` and `.github/` as belonging to no layer, and says that in this repository
  `Proposed` and `Accepted` records bind a change.
- `internal/verify` is the code that checks a token. Nothing else in the repository decides the outcome of the cases
  below. Before and after either change, it reads `kid` before it compares `exp` with the time of the check.

## The records

### ADR-0007: Verify every token in `Authorization` before policy evaluation

Status: Proposed.

Terms:

- **token**: the value after `Bearer ` in the `Authorization` header of a request.

Rules:

- **R4** (`verify`). A token whose header has a `kid` and whose `exp` is earlier than the time of the check is refused
  with HTTP 401 and the reason code `TOKEN_EXPIRED`.
- **R5** (`verify`). A token whose header has no `kid` is refused with HTTP 401 and the reason code `TOKEN_KID_MISSING`.

Open points:

- **O1.** How long after its `exp` a token is still accepted, to absorb clock skew between the issuer and the service.
  The answers under consideration are 0 seconds and 30 seconds. The security architect decides. Affects R4.

## The changes

Before either change, `internal/verify` refuses a token whose `exp` is earlier than the time of the check with HTTP 401
and `TOKEN_EXPIRED`, and refuses a token with no `kid` with HTTP 401 and `TOKEN_KID_MISSING`.

Change A deletes the comparison of `exp` with the time of the check. After it, a token whose `exp` passed an hour ago
is accepted. Nothing else changes. Its commit message and description carry no trailers.

Change B keeps the comparison and adds a 30-second allowance to it. After it, a token whose `exp` passed 10 seconds ago
is accepted, and a token whose `exp` passed 40 seconds ago is refused with HTTP 401 and `TOKEN_EXPIRED`. Nothing else
changes. Its commit message and description carry no trailers.
