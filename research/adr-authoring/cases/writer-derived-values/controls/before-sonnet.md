### File: docs/adr/0001-refuse-uploads-larger-than-the-upload-limit.md

````markdown
# Refuse an upload larger than the upload limit, which `UPLOAD_MAX_MB` sets in megabytes

## Status

Proposed

### Owner

`@media-lead`

### Participants and approvers

- Platform team: approves R1 to R5.

## Context

`POST /files`, handled in `internal/upload`, stores each uploaded file in the object store. Nothing limits the size of
an upload.

`internal/config` reads the settings from environment variables in `loadSettings`. For each integer setting,
`loadSettings` calls `strconv.ParseInt(value, 10, 32)` and stores the result in an `int32`. A setting that holds a
size in megabytes therefore tops out at 2147483647.

## Decision

We will refuse an upload larger than the upload limit with HTTP 413 before its body is stored. The operator sets the
limit in megabytes with `UPLOAD_MAX_MB`, and its default is 25.

### Terms

- **upload size**: the number of bytes in the body of a `POST /files` request.
- **upload limit**: `UPLOAD_MAX_MB` multiplied by `<bytes per MB>`, in bytes. O1 settles the factor.
- **stops the start**: the process exits before it serves a request. `loadSettings` meets a rule that uses this term by
  returning an error.

### Rules

#### Refusing an upload

- **R1** (`upload`). The `POST /files` handler answers HTTP 413 to a request whose upload size is greater than the
  upload limit, and no part of that request's body is stored in the object store.
- **R4** (`upload`). When the `POST /files` handler answers HTTP 413 under R1, it logs
  `file too large: got <n> MB, limit <m> MB` at `info` level. O2 settles how `<n>` is derived.
- **R5** (`upload`). The `POST /files` handler compares the upload size with the upload limit in a type that holds
  `2147483647` multiplied by `<bytes per MB>` without overflow.

#### The `UPLOAD_MAX_MB` setting

- **R2** (`config`). `loadSettings` reads the upload limit from `UPLOAD_MAX_MB`, in whole megabytes, and uses 25 where
  `UPLOAD_MAX_MB` is not set.
- **R3** (`config`, `main`). A value of `UPLOAD_MAX_MB` stops the start where the value is not a base-10 integer, is
  greater than `2147483647`, or is less than 1. O3 settles the lower bound.

### Confirmation

- **R1**: an integration test in `test/integration` uploads a file one byte larger than the upload limit and expects
  HTTP 413. CI runs it.
- **R3**: a CI test starts the service with `UPLOAD_MAX_MB=abc` and expects the process to exit before it serves a
  request.

### Implementation notes

Adds no requirement. Keep `UPLOAD_MAX_MB` as an `int32` in `loadSettings`, so that `strconv.ParseInt(value, 10, 32)`
enforces the upper bound of R3. Convert the value to `int64` before multiplying by `<bytes per MB>` (R5). Where the
request carries no `Content-Length`, count the bytes while reading the body, and stop reading once the count passes the
upload limit.

### Justification

A refusal before the body is stored keeps an oversized file out of the object store (R1). A value that stops the start
shows a misconfiguration when the service starts, and not on the first upload that depends on it (R3).

## Consequences

Negative:

- An upload larger than the upload limit is refused, and a client that sent such files before now receives HTTP 413
  (R1).
- A value of `UPLOAD_MAX_MB` that R3 names stops the service from starting, and the service does not fall back to the
  default.

Follow-ups:

- Write a record for the change to `loadSettings`: it collects every invalid setting, returns them in one error, and
  `main` logs that error at `error` level before it exits. The meeting notes list it, and it covers every setting, so it
  has its own reason to change.
- Write a record for the move of the integration tests in `test/integration` from the in-memory fake of the object store
  to a MinIO container.

## Open points

- **O1.** How many bytes make one MB in `UPLOAD_MAX_MB`: 1000000 or 1048576? The owner, `@media-lead`, decides. It
  affects R1, R4, R5, and the test under R1, which needs the exact upload limit.
- **O2.** How `<n>` in the log message of R4 is derived, since the handler may not know the full size of a body that it
  stops reading: the exact size, a size rounded up to a whole MB, or the number of megabytes read when the handler
  stopped. `@media-lead` decides. It affects R4.
- **O3.** The meeting notes give the upper bound of `UPLOAD_MAX_MB` and leave out `0` and negative values.
  `strconv.ParseInt` accepts them. R3 assumes that they stop the start. The alternative is that `0` means no upload is
  accepted, or that no limit applies. `@media-lead` decides. It affects R3.
````

### Message to the user

I wrote one record for the upload limit, `docs/adr/0001-refuse-uploads-larger-than-the-upload-limit.md`. Its status is `Proposed`, because three open points block acceptance.

**Questions**

- **O1:** Is one MB 1000000 or 1048576 bytes? The test "one byte over the limit" needs the exact value. The rules carry the placeholder `<bytes per MB>` until you answer.
- **O2:** What is `<n>` in `file too large: got <n> MB, limit <m> MB` when the handler stops reading a body of unknown size? It could be the exact size, a rounded-up size, or the megabytes read so far.
- **O3:** What should `UPLOAD_MAX_MB=0` or a negative value do? The notes don't say, and `ParseInt` accepts both. R3 assumes that they stop the start.
- Do you want a reading guide (`docs/adr/README.md`) and an `AGENTS.md` paragraph? A guide commits the team to ending every commit message and pull request description for code under the mapped paths with `Implements:` and `Defers:` trailers. I added neither. Without a guide, the rules still bind changes once the record is `Accepted`, and no change owes the trailers. The rules use the layer tags `upload`, `config`, and `main`, which are placeholders for a guide's layer names.
- Who is the platform team's contact account? The record names only "Platform team" as approver of R1 to R5.

**Split from the notes**

I left two items out of this record. Each has a different reason to change, and I listed both under Follow-ups. Do you want me to write them as separate records?

1. `loadSettings` collects every invalid setting into one error, and `main` logs it at `error` level. It covers all settings, not only the upload limit.
2. The integration tests move from the in-memory fake to a MinIO container.

**Other points**

- The notes give no reasons, so the Justification states only what follows from the rules. Add the platform team's reasons if you have them.
- R5 is my addition. It requires the size comparison to use a type that doesn't overflow, because `UPLOAD_MAX_MB` is an `int32`. Remove it if you don't want it.
- The two CI tests are named under Confirmation for R1 and R3. R2, R4, and R5 have no check yet, so they have no entry.
- I left out the Date heading, as the skill says to until the record is accepted.
