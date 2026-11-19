### File: docs/adr/0001-refuse-uploads-over-the-size-limit.md

````markdown
# Refuse an upload larger than the limit in `UPLOAD_MAX_MB` with HTTP 413

## Status

Proposed

### Owner

`@media-lead`

### Participants and approvers

- Platform team, account not given: approves R1 to R5.

## Context

The service stores files that users upload with `POST /files`. `internal/upload` handles that endpoint, and
`internal/config` reads the settings from environment variables in `loadSettings`. `loadSettings` parses each integer
setting with `strconv.ParseInt(value, 10, 32)` and stores it in an `int32`.

## Decision

We will refuse an upload larger than a limit with HTTP 413 before the service stores its body, and we will set the limit
in megabytes with the `UPLOAD_MAX_MB` setting, which defaults to 25.

### Terms

- **upload**: a request to `POST /files`.
- **upload size**: the number of bytes in the body of an upload.
- **limit**: the value of `UPLOAD_MAX_MB` multiplied by `<bytes per MB>` (O1), in bytes.
- **MB**: the unit that `<bytes per MB>` defines (O1). Messages and the setting use it with that meaning.
- **stops the start**: the process exits before it serves a request. The code that reads the settings meets this by
  returning an error to the entry point.

### Rules

#### Refusing an upload

- **R1** (`upload`). The service refuses an upload whose upload size is greater than the limit with HTTP status 413, and
  stores no byte of its body. An upload whose upload size is equal to or less than the limit is not refused for its
  size.
- **R2** (`upload`). When the service refuses an upload under R1, it logs one entry at `info` level that states the
  upload size and the limit, both in MB.

#### The setting

- **R3** (`config`). The limit comes from the setting `UPLOAD_MAX_MB`, which holds a whole number of MB.
- **R4** (`config`). Where `UPLOAD_MAX_MB` is not set, `UPLOAD_MAX_MB` is 25.
- **R5** (`config`). A value of `UPLOAD_MAX_MB` that is not a decimal integer, or that the integer type of the setting
  cannot hold, stops the start.

### Implementation notes

Adds no requirement. Test R1 with an upload one byte over the limit that expects 413, and with an upload of exactly the
limit that expects success. Test R5 by starting the service with `UPLOAD_MAX_MB=abc` and expecting it to stop. The
integration tests in `test/integration` can run these cases.

### Justification

An upload that is refused before the service stores its body leaves nothing to delete from the object store (R1). A
default of 25 lets an installation that sets nothing run with a known limit (R4). A value that cannot be read as the
limit stops the start, so the service never runs with a limit that nobody chose (R5).

### Alternatives considered

- **A1. Store the body, then delete it when its size turns out to be over the limit.** Rejected by R1: the service
  would store a body that it then has to remove.
- **A2. Use the default of 25 when `UPLOAD_MAX_MB` is not a number.** Rejected by R5: the service would run with a limit
  that the operator did not set.

## Consequences

Negative:

- An installation whose `UPLOAD_MAX_MB` is not a decimal integer, or is too large for the integer type of the setting,
  stops at start (R5).

Follow-ups:

- Write a record for the change to `loadSettings`: it collects every invalid setting into one error, and `main` logs
  that error at `error` level before it exits.
- Write a record for moving the tests in `test/integration` from the in-memory fake of the object store to a MinIO
  container.
- Add the tests named under **Implementation notes** to CI, then add them to **Confirmation**.

## Open points

- **O1.** What is one MB: 1000000 bytes or 1048576 bytes? The platform team decides. It affects R1, R2, and R3, and
  decides which upload is one byte over the limit.
- **O2.** What happens for a value of `UPLOAD_MAX_MB` that is 0, negative, or empty? The answers under consideration
  are: it stops the start, or 0 means no uploads are accepted. The platform team decides. It affects R5.
- **O3.** Did an earlier version of the service enforce another limit or none? Where an installation upgrades, it gets
  the default in R4 unless a rule says otherwise. The platform team decides. It affects R4 and the Negative
  consequences.
````

### Message to the user

I wrote one record, `docs/adr/0001-refuse-uploads-over-the-size-limit.md`. It has status `Proposed`, because it has three open points. I left out the Date heading until the team accepts it.

**Split.** The meeting notes cover three decisions that change for different reasons. I wrote only the upload limit and listed the other two under Follow-ups:
- `loadSettings` collects every invalid setting into one error, and `main` logs it at `error` level.
- The integration tests move from the in-memory fake to MinIO.

Do you want me to draft those two records?

**Kept out of the rules**
- The largest value `int32` holds, 2147483647, only restates the code. R5 states the decision instead: a value the setting's type cannot hold stops the start.
- The text `file too large: got <n> MB, limit <m> MB` is not a rule. R2 requires only the `info` level and the size and the limit in MB. If an alert or log query matches that text, tell me and I'll add a rule for the exact wording.
- The two CI tests test R1 and R5, so they aren't rules. I put them in Implementation notes. Add them to Confirmation when they land.

**Questions**
1. What is one MB: 1000000 bytes or 1048576 bytes? "One byte over the limit" depends on the answer (O1).
2. What should a value of 0, a negative number, or an empty string for `UPLOAD_MAX_MB` do (O2)?
3. Did earlier versions enforce a different limit? That decides what an upgrading installation gets (O3).
4. What are the platform team's account and the accounts of its approvers? The record only says "platform team, account not given".
5. The repository has no reading guide, so no change owes the `Implements` and `Defers` trailers. Do you want me to add a `docs/adr/README.md` guide and an agent-instructions paragraph? That would commit the team to ending every commit message and pull request description with those trailers for code under the mapped paths.
