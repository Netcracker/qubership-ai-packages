# Task

Check the pull request below against the repository's architecture decision records.

Give a heading `## Change`, then a Markdown table with one row per rule that your check walks: the rule as
`ADR-NNNN Rn`, its verdict, and one line of reason. After the table, list anything the report names apart from the
verdicts, and any rule you did not walk, with the reason.

The facts below were checked against the code; treat every fact in them as verified, and add none that they do not
carry.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- `docs/adr/` holds the records. `docs/adr/README.md` is the reading guide: it maps the layer `keys` to
  `internal/keys/`, lists `docs/adr/` and `.github/` as belonging to no layer, and says that `Accepted` records bind a
  change. Issues #300 and #301 are open.
- `internal/keys` is the code that loads and holds the signing keys of each key source. Nothing else in the repository
  decides the outcome of the cases below.

## The records

### ADR-0010: Hold the signing keys of each key source in memory

Status: Accepted. Date: 2026-09-14.

Rules:

- **R7** (`keys`). A loaded key set stays in use for 5 minutes; the first token that needs the key set after that
  reloads it from its source.
- **R9** (`keys`). The service loads the key set of every key source at startup, before it accepts a request.

### ADR-0020: Reload signing keys sooner

Status: Proposed.

Related ADRs:

- ADR-0010: this record replaces ADR-0010 R7.

Rules:

- **R3** (`keys`). A loaded key set stays in use for 1 minute; the first token that needs the key set after that
  reloads it from its source.

## The change

Before the change, `internal/keys` loads the key set of a key source on the first token that needs it, not at startup,
keeps it for 5 minutes, and then reloads it on the first token that needs it.

The change deletes the expiry of a loaded key set. After it, a key set loaded once stays in use until the process
restarts, and no token reloads it. The first load still happens on the first token that needs it, and nothing else
changes.

The change ends its commit message and its description with:

```text
Defers: ADR-0020 R3 to #300; ADR-0010 R9 to #301
```
