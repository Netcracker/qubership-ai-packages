### File: docs/adr/0001-refuse-uploads-over-a-configured-size-limit.md

````markdown
# Refuse an upload larger than `UPLOAD_MAX_MB` megabytes with HTTP 413

## Status

Proposed

### Owner

`media-lead`

### Participants and approvers

- Owner, `media-lead`: approves R1 to R4.
- Platform team: approves R1 to R4.

## Context

`example/media-store` is a Go service that stores files that users upload over HTTP. `internal/upload` handles
`POST /files` and writes each upload to an object store.

`internal/config` reads the service's settings from environment variables in `loadSettings`. It parses each integer
setting with `strconv.ParseInt(value, 10, 32)` and stores the result in an `int32`.

## Decision

We will refuse a `POST /files` request whose upload is larger than a limit set in megabytes by `UPLOAD_MAX_MB`. The
service refuses the request with HTTP 413 before it stores the upload, and an invalid value of `UPLOAD_MAX_MB` stops
the start.

### Terms

- **upload**: the body of a `POST /files` request.
- **megabyte**: `<bytes per megabyte>` bytes (O1).
- **upload limit**: the number of megabytes that R3 sets.
- **unset**: `UPLOAD_MAX_MB` is unset when the environment has no variable of that name, or when its value is the empty
  string (O2).
- **stops the start**: the process exits before it serves a request. `loadSettings` meets a rule that requires this
  outcome by returning an error.

### Rules

#### Refusing an upload

- **R1** (`upload`). `internal/upload` refuses a `POST /files` request whose upload is larger than the upload limit
  with HTTP 413, and stores no byte of that upload in the object store.
- **R2** (`upload`). When `internal/upload` refuses a request under R1, it logs `file too large: got <n> MB, limit <m> MB`
  at `info` level. `<m>` is the upload limit in megabytes, and `<n>` is the size of the upload in megabytes (O3, O4).

#### The `UPLOAD_MAX_MB` setting

- **R3** (`config`). The service reads the upload limit, as a whole number of megabytes, from the environment variable
  `UPLOAD_MAX_MB`. When `UPLOAD_MAX_MB` is unset, the upload limit is 25 megabytes.
- **R4** (`config`). A value of `UPLOAD_MAX_MB` that is not a whole number, or that the type of the setting cannot hold,
  stops the start (O2).

### Implementation notes

Adds no requirement. Compute the limit in bytes as an `int64`: the largest value an `int32` setting holds, multiplied by
the bytes in a megabyte, does not fit in an `int32`. Refuse the request at once when its `Content-Length` is larger than
the limit. Otherwise, read the body through `http.MaxBytesReader` with the limit, and refuse the request when the reader
reports that the body went past it, before the service writes anything to the object store.

`strconv.ParseInt(value, 10, 32)` already returns an error for a value that is not a number, or that an `int32` cannot
hold. `loadSettings` meets R4 when it returns that error for `UPLOAD_MAX_MB`.

Two CI tests are planned. One uploads a file one byte larger than the upload limit and expects HTTP 413 (R1). The other
starts the service with `UPLOAD_MAX_MB=abc` and expects the process to exit before it serves a request (R4). Each test
joins **Confirmation** when it lands.

### Justification

HTTP 413 (Content Too Large, RFC 9110 section 15.5.14) is the status that HTTP defines for a request body larger than
the server accepts, so a client can tell this refusal from other failures (R1). Because the service refuses the request
before it stores the upload, an oversized upload uses no space in the object store, and the service has nothing to
delete afterwards (R1).

A refused upload is a client error that the service handles, not a failure of the service, so it is logged at `info`
level (R2). The default lets an installation run without setting `UPLOAD_MAX_MB` (R3). An invalid value stops the start,
so the operator finds the mistake when the service is deployed, not at the first upload (R4).

### Alternatives considered

- **A1. Store the upload, then check its size and delete it from the object store when it is too large.** Rejected by
  R1: the oversized upload is written to the object store before it is refused.
- **A2. Use the default of 25 megabytes when `UPLOAD_MAX_MB` holds an invalid value.** Rejected by R4: the service would
  run with a limit that the operator did not set, and nothing would stop the deployment.

## Consequences

Negative:

- An installation that leaves `UPLOAD_MAX_MB` unset refuses every upload larger than 25 megabytes after the upgrade
  (R3).
- A client that sends an upload larger than the upload limit gets HTTP 413 and has to handle it (R1).

## Open points

- **O1.** How many bytes is a megabyte? The answers are 1000000 (MB) or 1048576 (MiB). `media-lead` decides. It affects
  R1, R2, and R3, and the byte count of the CI test that uploads one byte over the limit.
- **O2.** What happens when `UPLOAD_MAX_MB` is zero, negative, or the empty string? `strconv.ParseInt` accepts `0` and
  negative numbers. For zero and negative values, the answers are: they stop the start, or `0` means that every upload is
  refused. For the empty string, the answers are: it counts as unset, as **unset** assumes, or it stops the start.
  `media-lead` decides. It affects R3 and R4.
- **O3.** What is `<n>` in R2 when the request has no `Content-Length`, and how is it rounded? Without
  `Content-Length`, the service stops reading at the limit and does not learn the full size of the upload. The answers
  are: the bytes read so far, rounded up to whole megabytes, or a fixed marker such as `unknown`. `media-lead` decides.
  It affects R2.
- **O4.** Does an alert, a dashboard, or a log query match the text of the log line in R2? If one does, R2 keeps the
  text. If none does, R2 keeps only the `info` level, and the text becomes a choice of the code. `media-lead` decides.
  It affects R2.
````

### Message to the user

I wrote the record as `docs/adr/0001-refuse-uploads-over-a-configured-size-limit.md`. Its status is `Proposed`. The repository has no records yet, so it follows the default layout.

**Two decisions from the notes are left out of this record.** Each one changes for a different reason than the upload limit, so I'd give each its own record:

1. **Reporting invalid settings:** `loadSettings` collects every invalid setting and returns them in one error, and `main` logs that error at `error` level before it exits. This applies to all settings, not just `UPLOAD_MAX_MB`.
2. **Integration test backend:** `test/integration` moves from the in-memory fake to a MinIO container, so the tests run against a real S3 API.

Should I write these as records 0002 and 0003?

**The int32 maximum isn't a rule.** The notes give 2147483647 as the largest value. I didn't write that number into a rule because it only describes the current type. R4 says instead that a value the setting's type cannot hold stops the start, which still holds if the type changes.

**The two CI tests aren't rules either.** They only test R1 and R4, so they're listed under **Implementation notes**. Each one moves to **Confirmation** when it lands.

**Four open points block acceptance.** Could `media-lead` answer them?
- **O1:** Is a megabyte 1000000 or 1048576 bytes?
- **O2:** What should zero, negative, and empty values of `UPLOAD_MAX_MB` do?
- **O3:** What should `<n>` be in the log line when the request has no `Content-Length`?
- **O4:** Does any alert or log query match the log text?

**Other questions:**
- What is the platform team's GitHub team handle? I need it for **Participants and approvers**.
- The meeting notes list no alternatives. A1 (store the upload, then delete it) and A2 (fall back to the default when the value is invalid) are mine. Should I keep them, replace them with the options the meeting actually discussed, or remove the section?
- Should I add a reading guide (`docs/adr/README.md`) and a paragraph in `AGENTS.md`? This commits the team to a process: every commit message and pull request description that changes code under the mapped paths must end with `Implements:` and `Defers:` trailers that name the rules it brings or postpones. Without a guide, changes are checked against accepted records but don't need the trailers.
