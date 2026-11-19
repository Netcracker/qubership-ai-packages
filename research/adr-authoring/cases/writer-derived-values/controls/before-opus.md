### File: docs/adr/0001-refuse-uploads-larger-than-upload-max-mb.md

````markdown
# Refuse uploads larger than `UPLOAD_MAX_MB` with HTTP 413

## Status

Proposed

### Owner

`@media-lead`

### Participants and approvers

- Owner, `@media-lead`: approves R1 to R4.
- Platform team, `<platform team account>`: approves R1 to R4.

## Context

The service `example/media-store` stores files that users upload over HTTP. `internal/upload` handles `POST /files` and
writes the body to an object store.

`internal/config` reads the settings from environment variables in `loadSettings`. For each integer setting,
`loadSettings` calls `strconv.ParseInt(value, 10, 32)` and stores the result in an `int32`. `strconv.ParseInt` returns
an error for a value that is not a decimal integer. With a bit size of 32, it also returns an error for a value outside
the `int32` range, so the largest value it accepts is 2147483647.

The service needs an upper bound on the size of an upload that it stores. Operators need to set that bound for each
installation.

## Decision

We will refuse with HTTP 413 any `POST /files` request whose upload is larger than a limit set in megabytes by
`UPLOAD_MAX_MB`, before the body is stored, and we will stop the start when `UPLOAD_MAX_MB` holds an invalid value.

### Terms

- **MB**: `<bytes per MB>` bytes. O1 asks for the value.
- **upload size**: the number of bytes in the body of a `POST /files` request. O3 names the assumption behind this
  extent.
- **limit**: the number of MB that R3 sets.
- **stops the start**: the process exits with a non-zero status before it serves a request. `loadSettings` meets a rule
  that requires this by returning an error.

### Rules

#### Refusing an upload

- **R1** (`upload`). When the upload size of a `POST /files` request is larger than the limit, the service responds
  with HTTP status 413, and the object store holds no object from that request. A `POST /files` request whose upload
  size equals the limit is not refused for its size.
- **R2** (`upload`). When the service refuses a `POST /files` request under R1, it logs
  `file too large: got <n> MB, limit <m> MB` at `info` level. `<m>` is the limit. `<n>` is the upload size in MB,
  rounded up to a whole number. Where the request carries no `Content-Length` header, `<n>` counts the bytes that the
  service read before it refused the request.

#### The setting

- **R3** (`config`). The environment variable `UPLOAD_MAX_MB` sets the limit as a whole number of MB. Where
  `UPLOAD_MAX_MB` is unset, the limit is 25.
- **R4** (`config`). A value of `UPLOAD_MAX_MB` stops the start where it is not a decimal integer, where it is larger
  than 2147483647, or where it is below 1. An empty value is not a decimal integer.

### Implementation notes

Adds no requirement.

In `internal/upload`, compare `Content-Length` with the limit before the handler reads the body. Then wrap the body in
`http.MaxBytesReader` with the limit in bytes, so that a request without `Content-Length` is cut off one byte past the
limit. Map `*http.MaxBytesError` to 413. Where the handler streams the body to the object store as it reads, abort the
write when the reader returns that error, so that no partial object stays behind. The limit in bytes, 2147483647 times
1048576 at most, fits in an `int64`.

In `internal/config`, `strconv.ParseInt(value, 10, 32)` already rejects a value that is not a decimal integer and a
value larger than 2147483647. Add a check for a value below 1.

CI gets two tests. The first uploads a file one byte larger than the limit and expects 413. The second starts the
service with `UPLOAD_MAX_MB=abc` and expects it to exit. When each test lands, add it under **Confirmation**, for R1 and
R4 respectively.

### Justification

A refusal before the body is stored keeps an oversized file out of the object store, both as a complete object and as
a partial write (R1). HTTP 413 is the status that RFC 9110 defines for a request body larger than the server accepts,
so clients handle it without code specific to this service (R1).

A refused upload is a client error that the service handles, so it is logged at `info` level. The message carries both
sizes, so an operator can tell from the log whether the limit is too low for the uploads users send (R2).

A limit in MB keeps the setting short to write and easy to read. An `int32` matches how `loadSettings` parses every
other integer setting (R3, R4). A service that stops the start on an invalid value makes a typo visible at deploy time.
A service that fell back to the default would run with a limit that no operator chose (R4).

### Alternatives considered

- **A1. Fall back to the default of 25 when `UPLOAD_MAX_MB` is invalid.** Rejected by R4: the service would start with a
  limit that the operator did not set, and only a log line would show it.
- **A2. Set the limit in bytes with an `int32` setting.** The largest limit would be just under 2 GiB (2147483647
  bytes), and every value would be a long number that is easy to mistype.
- **A3. Store the body first, then delete the object when it is larger than the limit.** Rejected by R1: the object
  store would hold the object until the delete ran, and a failed delete would leave it there.

## Consequences

Negative:

- An installation that upgrades without setting `UPLOAD_MAX_MB` refuses every upload larger than 25 MB (R3). Where such
  an installation accepted larger uploads before, those uploads now get 413.
- An installation whose `UPLOAD_MAX_MB` holds an invalid value no longer runs after the upgrade (R4).

Follow-ups:

- Add the two CI tests under **Confirmation** when they land.
- Write a record for the collection of every invalid setting into one error in `loadSettings`, and for the `error` log
  in `main`.
- Write a record for the move of the integration tests in `test/integration` from the in-memory fake to a MinIO
  container.

## Open points

- **O1.** How many bytes is one MB: 1000000 or 1048576? `@media-lead` decides. Affects R1, R2, and R3 through the term
  **MB**, and the size of the file in the test that uploads one byte over the limit.
- **O2.** R4 assumes that a value below 1 stops the start. The other answer is that 0 turns the limit off and a negative
  value stops the start. `@media-lead` decides. Affects R1 and R4.
- **O3.** The term **upload size** assumes that the limit applies to the whole request body. If `POST /files` takes a
  multipart body, the other answer is that the limit applies to the bytes of the file part alone. `@media-lead` decides.
  Affects R1 and R2.
- **O4.** R2 assumes that `<n>` is rounded up, so a file one byte over a 25 MB limit logs `got 26 MB`. The other answers
  are to round down or to log a decimal value. `@media-lead` decides. Affects R2.
````

### Message to the user

I wrote ADR-0001 in `docs/adr/`, the default location since the repository has no records yet. Its status is `Proposed`. The platform team has approved the decision, but the record can't be set to `Accepted` until open points O1 to O4 are settled:

- **O1:** whether one MB is 1000000 or 1048576 bytes. The one-byte-over test depends on this too.
- **O2:** whether `UPLOAD_MAX_MB=0` or a negative value stops the start. I assumed it does.
- **O3:** whether the limit applies to the whole request body or only to the file part of a multipart body. I assumed the whole body.
- **O4:** how `<n>` in the log message is rounded. I assumed it rounds up.

The record has no **Confirmation** section yet because neither CI test exists. Implementation notes describe both tests, and each one goes under **Confirmation** when it lands.

The notes named no rejected options, so I wrote A1 to A3 under **Alternatives considered** to explain the rules. Please confirm them or drop them.

I left two items from the notes out of this record. Each is a separate decision with its own reason to change:

1. **Collecting every invalid setting into one error.** This means `loadSettings` returns all invalid settings in one error and `main` logs it at `error` level. It covers every setting, not only the upload limit. R4 only needs an invalid `UPLOAD_MAX_MB` to stop the start.
2. **Moving the integration tests from the in-memory fake to a MinIO container.** This is a choice about test infrastructure.

Should I write ADR-0002 and ADR-0003 for these?

Questions:

1. What is the platform team's GitHub account? The record has a `<platform team account>` placeholder for it.
2. Should I add a reading guide in `docs/adr/README.md`, plus a paragraph in the agent instructions that points to it? The guide maps `internal/upload`, `internal/config`, and the tests to layers. It also commits the team to ending every commit message and pull request description that changes that code with the `Implements:` and `Defers:` trailers. Without the guide, changes are still checked against the rules, but no change has to carry the trailers.
