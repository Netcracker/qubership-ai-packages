# Task

Write an architecture decision record for the decision in the meeting notes below, in the repository described below.

Give every file you would create or change as a heading `### File: <path>`, followed by the file's full content in a
fence of four backticks. Then give a heading `### Message to the user` with what you would tell the user. Ask nothing
and wait for nothing: where you would ask the user something, write the question in that message.

## Repository facts

- Repository: example/token-gate, a Go service that checks the token of each request before policy evaluation.
- The repository has no architecture decision records yet: no `docs/adr/`, no `docs/decisions/`, and no `README.md`
  that describes records.
- `internal/policyclient` is the code that calls the policy service over HTTP. `internal/handler` turns its errors into
  responses.

## Meeting notes

- When the call to the policy service fails, we retry a few times before we give up.
- Each call to the policy service times out after 5 seconds.
- When every retry has failed, the request is refused with HTTP 503 and the reason code `POLICY_UNAVAILABLE`.
- The platform team approves this. Who owns the record is not settled yet.
