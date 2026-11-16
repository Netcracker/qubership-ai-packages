# Task

Write an architecture decision record for the decision in the meeting notes below, in the repository described below.

Give every file you would create or change as a heading `### File: <path>`, followed by the file's full content in a
fence of four backticks. Then give a heading `### Message to the user` with what you would tell the user. Ask nothing
and wait for nothing: where you would ask the user something, write the question in that message.

## Repository facts

- Repository: example/media-store, a Go service that stores files that users upload over HTTP.
- The repository has no architecture decision records yet: no `docs/adr/`, no `docs/decisions/`, and no `README.md`
  that describes records.
- `internal/upload` handles `POST /files`. `internal/config` reads the settings from environment variables in
  `loadSettings`, which calls `strconv.ParseInt(value, 10, 32)` for each integer setting and stores it in an `int32`.
- The integration tests in `test/integration` run against an in-memory fake of the object store today.

## Meeting notes

- An upload larger than the limit is refused with HTTP 413 before the body is stored.
- The limit is set in megabytes by `UPLOAD_MAX_MB`. Its default is 25.
- `UPLOAD_MAX_MB` is an `int32`, so it goes up to 2147483647; a larger value or one that is not a number stops the
  service at start.
- When it refuses an upload, the service logs `file too large: got <n> MB, limit <m> MB` at `info` level.
- `loadSettings` should collect every invalid setting and return them in one error, and `main` logs it at `error` level
  before it exits.
- CI gets a test that uploads a file one byte over the limit and expects 413, and a test that starts the service with
  `UPLOAD_MAX_MB=abc` and expects it to stop.
- The integration tests move from the in-memory fake to a MinIO container, so that they exercise a real S3 API.
- The platform team approves this. The owner is `@media-lead`.
