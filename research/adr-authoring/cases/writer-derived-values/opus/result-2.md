### File: docs/adr/0001-limit-upload-size.md

````markdown
# Refuse an upload larger than `UPLOAD_MAX_MB` megabytes with HTTP 413 before storing it

## Status

Proposed

### Owner

`@media-lead`

### Participants and approvers

- Owner, `@media-lead`: approves R1 to R4.
- Platform team: approves R1 to R4.

## Context

`example/media-store` stores files that users upload with `POST /files`, which `internal/upload` handles. The service
has no setting that limits the size of an upload.

`internal/config` reads the settings from environment variables in `loadSettings`. It parses each integer setting with
`strconv.ParseInt(value, 10, 32)` and stores it in an `int32`, so the largest value an integer setting holds is
2147483647.

The integration tests in `test/integration` run against an in-memory fake of the object store.

## Decision

We will refuse an upload whose size is larger than a limit set in megabytes by `UPLOAD_MAX_MB`. The service responds
with HTTP 413 before it stores any of the body.

### Terms

- **MB**: `<bytes per MB>` bytes.
- **upload size**: the number of bytes in the body of a `POST /files` request.
- **limit**: the value of `UPLOAD_MAX_MB` multiplied by the number of bytes in an MB.
- **stops the start**: the process exits before it serves a request. `loadSettings` meets a rule that uses this term by
  returning an error.

### Rules

#### Refusing an upload

- **R1** (`upload`). When the upload size of a `POST /files` request is larger than the limit, the service responds
  with HTTP 413 and writes no byte of the request body to the object store.
- **R2** (`upload`). When the service refuses an upload under R1, it logs `file too large: got <n> MB, limit <m> MB` at
  `info` level, where `<n>` is the upload size in MB and `<m>` is the value of `UPLOAD_MAX_MB`.

#### The setting

- **R3** (`config`). The environment variable `UPLOAD_MAX_MB` sets the limit as a whole number of MB. When
  `UPLOAD_MAX_MB` is not set or is empty, its value is 25.
- **R4** (`config`). A value of `UPLOAD_MAX_MB` that is not an integer, that the type of the setting cannot hold, or
  that is less than 1 stops the start.

### Implementation notes

Adds no requirement. Refuse a request whose `Content-Length` is larger than the limit before reading the body. For a
body without a `Content-Length`, wrap it in `http.MaxBytesReader` with the limit, and write to the object store only
after the read stays within the limit. Compute the limit in bytes as an `int64`, because 2147483647 MB in bytes
overflows an `int32`.

Two tests in CI would cover the main cases. The first uploads a body one byte larger than the limit, then expects HTTP
413 and an empty object store (R1). The second starts the service with `UPLOAD_MAX_MB=abc` and expects it to exit
before it serves a request (R4).

### Justification

Refusing the upload before any byte reaches the object store means a refused upload leaves no partial object and costs
no storage (R1). A refused upload is a client error that the service handles, not a failure of the service, so the log
line is at `info` level (R2). An invalid value stops the start, so an operator finds a mistyped value when the
deployment fails, not later from uploads that are refused or accepted by mistake (R4).

### Alternatives considered

- **A1. Store the body, then delete the object when it turns out to be larger than the limit.** Rejected by R1: the
  object store receives the bytes, and a failed delete leaves the object behind.
- **A2. Use the default of 25 MB when `UPLOAD_MAX_MB` is not a valid number.** Rejected by R4: a mistyped value would
  quietly set a limit the operator did not choose.

## Consequences

Positive:

- A mistyped `UPLOAD_MAX_MB` fails the deployment that introduces it (R4).

Negative:

- After the upgrade, an installation that does not set `UPLOAD_MAX_MB` refuses every upload larger than 25 MB, which it
  accepted before (R3).
- An installation that sets `UPLOAD_MAX_MB` to a value that R4 rejects stops the start after the upgrade.

## Open points

- **O1.** How many bytes is an MB: 1000000 or 1048576? `@media-lead` decides. Affects the terms **MB** and **limit**,
  and so R1 to R3.
- **O2.** R4 assumes that a value less than 1 stops the start, and R3 assumes that an empty value counts as not set.
  The alternatives are that 0 turns the limit off, or that an empty value stops the start. `@media-lead` decides.
  Affects R3 and R4.
- **O3.** Does an alert or a log query match the text `file too large: got <n> MB, limit <m> MB`? If one does, R2
  keeps the text, and the record still needs to say how `<n>` is rounded, such as up to a whole MB. If none does, R2
  keeps only the `info` level, and the text is left to the code. `@media-lead` decides. Affects R2.
- **O4.** R1 assumes that the upload size counts the whole request body. The alternative is to count only the bytes of
  the file, without any multipart framing. `@media-lead` decides. Affects R1 and R2.
````

### Message to the user

I wrote `docs/adr/0001-limit-upload-size.md` with the status `Proposed`. The platform team has approved the decision, but open points O1 to O4 block acceptance until they're answered.

**Two decisions are not in this record.** They answer different questions and would change for different reasons, so I propose a separate record for each:

- `loadSettings` collects every invalid setting and returns them in one error, and `main` logs that error at `error` level before it exits. This covers how every setting reports errors, not only `UPLOAD_MAX_MB`.
- The integration tests move from the in-memory fake to a MinIO container, so they run against a real S3 API. This decides how the service is tested.

Should I write those two records?

**Some notes aren't rules:**
- **CI tests:** The two tests (one byte over the limit expects 413, and `UPLOAD_MAX_MB=abc` expects the service to stop) only check R1 and R4. They join a **Confirmation** section once they land, and until then they appear under **Implementation notes**.
- **Upper bound:** The value 2147483647 is the largest value an `int32` holds, so R4 says "a value the type of the setting cannot hold" instead of the number. **Context** gives the number.

**Questions for you:**

1. What is the GitHub account of the platform team, for **Participants and approvers**?
2. O1: Is an MB 1000000 bytes or 1048576 bytes?
3. O2: Should a value of 0 or less stop the start, or should 0 turn the limit off? Should an empty `UPLOAD_MAX_MB` use the default of 25, or stop the start?
4. O3: Does an alert or a log query match `file too large: got <n> MB, limit <m> MB`? If so, how is `<n>` rounded?
5. O4: Does the upload size count the whole request body or only the file's bytes?
6. Should I add a reading guide in `docs/adr/README.md` that maps `internal/upload` and `internal/config` to the `upload` and `config` layers? It commits the team to a process: every change to code under those paths ends its commit message and pull request description with `Implements:` and `Defers:` trailers that name the rules of the records.
