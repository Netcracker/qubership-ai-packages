### File: docs/adr/0001-upload-size-limit.md

````markdown
# Refuse an upload larger than a configurable size limit with HTTP 413

## Status

Proposed

### Owner

`@media-lead`

### Participants and approvers

- Platform team, `<platform team account>`: approves R1 to R4.

## Context

`POST /files` in `internal/upload` accepts files that users upload over HTTP and stores them in the object store.
`internal/config` reads the settings from environment variables in `loadSettings`. For each integer setting,
`loadSettings` calls `strconv.ParseInt(value, 10, 32)` and stores the result in an `int32`.

## Decision

We will refuse a `POST /files` upload larger than the upload limit with HTTP 413 before any of it is stored, and we
will set the upload limit in megabytes with `UPLOAD_MAX_MB`, which defaults to 25.

### Terms

- **upload limit**: the value of `UPLOAD_MAX_MB` multiplied by `<bytes per megabyte>`, in bytes. O1 asks for the
  multiplier.
- **upload size**: the number of bytes of file content in a `POST /files` request. O2 asks whether this is the right
  measure.
- **stops the start**: the process exits before it serves a request. `loadSettings` meets a rule that stops the start
  by returning an error.

### Rules

#### Refusing an upload

- **R1** (`upload`). A `POST /files` request whose upload size is larger than the upload limit is refused with HTTP
  413, and the service writes no part of its file content to the object store.
- **R4** (`upload`). The service logs each refusal under R1 at `info` level.

#### The setting

- **R2** (`config`). The upload limit is set by `UPLOAD_MAX_MB`, in megabytes. When `UPLOAD_MAX_MB` is not set, its
  value is 25.
- **R3** (`config`). A value of `UPLOAD_MAX_MB` that is not an integer written in base 10, or that the integer type of
  the setting cannot hold, stops the start.

### Confirmation

- **R1**: an integration test in `test/integration` uploads a file one byte larger than the upload limit and expects
  HTTP 413.
- **R3**: a CI test starts the service with `UPLOAD_MAX_MB=abc` and expects the process to exit.

### Implementation notes

Adds no requirement. The meeting settled this log text for a refusal: `file too large: got <n> MB, limit <m> MB`. O3
asks whether the text is part of the contract.

### Justification

Refusing before storing keeps an oversized file out of the object store (R1). A setting in megabytes with a default of
25 lets an operator change the limit without a new build (R2). A value that cannot be read as a limit stops the start,
so the service never runs with a limit nobody chose (R3). The notes give no further reasons.

### Alternatives considered

The meeting notes record no rejected alternative. O5 asks for them.

## Consequences

Negative:

- A file larger than 25 MB is refused with HTTP 413 unless an operator sets `UPLOAD_MAX_MB` (R1, R2). O4 asks what an
  existing installation gets on upgrade.
- A mistyped `UPLOAD_MAX_MB` stops the start instead of falling back to the default (R3).

## Open points

- **O1.** How many bytes is one megabyte: 1000000 or 1048576? `@media-lead` decides. It sets the extent of the upload
  limit and affects R1, R2, and the test under R1.
- **O2.** Assumption: the upload size counts the bytes of file content, not the whole request body with its multipart
  framing. `@media-lead` confirms. It affects R1.
- **O3.** Does an alert or log query match the text `file too large: got <n> MB, limit <m> MB`? If so, the text becomes
  a rule. `@media-lead` decides. It affects R4.
- **O4.** Did `POST /files` have a limit before this record? If it had none or a different one, a rule must state what
  an existing installation gets on upgrade. `@media-lead` decides. It affects R1 and R2.
- **O5.** Which alternatives did the meeting reject, and why? `@media-lead` answers. It affects Justification and
  Alternatives considered.
- **O6.** What happens for `UPLOAD_MAX_MB=0` or a negative value? The notes do not say. `@media-lead` decides between
  stopping the start and accepting the value. It affects R3.
````

### Message to the user

I wrote one record, `docs/adr/0001-upload-size-limit.md`, with status `Proposed`. The repository has no records yet, so I used the default location and numbering. I left out the Date heading because the record isn't accepted.

**Split.** The notes hold three decisions with different reasons to change. I wrote only the first and suggest two more records:
- Collecting every invalid setting into one error from `loadSettings`, and logging it at `error` level in `main` before the exit.
- Running the integration tests against a MinIO container instead of the in-memory fake.

Tell me if you want me to draft them. The record cites the existing `UPLOAD_MAX_MB=abc` behavior only through R3. It doesn't depend on the collected-error behavior.

**Choices I made.**
- The `int32` ceiling of 2147483647 is a detail of the code, so R3 states it as "a value the integer type of the setting cannot hold".
- The log text is in Implementation notes. R4 fixes only the `info` level.
- The two CI tests are entries under Confirmation, not rules.

**Questions** (also recorded as open points, O1 to O6):
1. Is 1 MB 1000000 or 1048576 bytes? The "one byte over" test needs the answer.
2. Does the limit count only the file content, or the whole request body?
3. Does an alert or log query match the log text? If so, I'll make the text a rule.
4. Did `POST /files` have a limit before this? If so, what should an existing installation get on upgrade?
5. Which alternatives did the meeting reject, and why? The notes give none.
6. What should `UPLOAD_MAX_MB=0` or a negative value do?
7. What is the platform team's account? I left it as a placeholder under approvers. The record can't become `Accepted` until the open points are closed.

I didn't add a `README.md` reading guide or an `AGENTS.md` paragraph. A guide commits the team to ending every commit message and pull request description with the `Implements` and `Defers` trailers for code under the layers it maps. Do you want that? If so, I'll map `internal/upload` and `internal/config` to layers and add the guide.
