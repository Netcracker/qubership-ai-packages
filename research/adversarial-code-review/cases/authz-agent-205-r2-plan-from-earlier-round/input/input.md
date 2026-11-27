# Review input: Netcracker/qubership-authz-agent#205, round 2

- URL: https://github.com/Netcracker/qubership-authz-agent/pull/205
- Title: feat(authz-agent)!: decide check, bulk, and filter requests with Rego generated per tenant
- Author: vlsi. Head branch vlsi:claude/rego-translator-stage6-871db2, base main. Open, not draft. kichasov CHANGES_REQUESTED 2026-11-05.
- Description (claims to verify, published 2026-11-27 against this head): `<work>/raw/body.md`.
- Request: round 2 of this reviewer. Review the whole change against main, not only the commits since round 1. Deliver locally only; nothing is published.

## Revision

- base e2c7029ef08ca1b5f68e9374b8ed41565f54a6b4 (current main; also the merge base)
- head 1872c610b0c7ab251f420543eaad1c8f6873fcfc
- 517 files changed (123 added, 111 modified, 283 deleted; 206 of the deletions are test/svt profiler scenarios). Code map: `<work>/shards/map.md` (22584 added lines of code, 25217 of tests; internal/regogen/agent-tables.json is 5770 lines of generated data exported from an executable specification).
- File list: `<work>/raw/files.txt`, `<work>/raw/numstat.txt`. Commits (165): `<work>/raw/commits.txt`.
- The change: `git -C <work>/ws diff e2c7029e...1872c610`.

## Workspace

- Isolated worktree at head, read-only for reviewers: `<work>/ws`. Add your own worktree to run anything.

## Stack

- Base branch main. Not stacked (checked in round 1; the branch was since merged with main). Related: #226 (ADRs), #232, #372 (request deadline / PIP timeouts, F36+F58 follow-up), #384 (ADR-0099 R12 filter bounds follow-up).

## History and discussion

- Round 1 of this reviewer at c8315157: `<work>/../round-1-c8315157/review.json` (92 findings F1–F92), ledger `<work>/../round-1-c8315157/ledger.md`. It was published on 2026-11-26 as a PR review (body https://github.com/Netcracker/qubership-authz-agent/pull/205#pullrequestreview-6073365080) with 76 inline threads; threads mapped to finding ids in `<work>/raw/threads-mapped.json`.
- Between rounds the author fixed findings in batches; disposition of every round-1 finding: `<work>/prev/round1-dispositions.md` (copied from the author's notes). Owner decisions (2026-11-27): F26 → 400 for a value too big to look up (27bbeda3); a MAPPING value too big to look up is a failed source (1872c610); default tenant unresolved → 503 DEFAULT_TENANT_NOT_TRANSLATED with Retry-After (725a2fd4, "R22"); F83 → entitlements and permission scope called with GET and no body (0807ce3c); F58 → README states the worst-case wait, deadline tracked in #372 (cc21ad02); F75 → regogen-corpus and regogen-locality moved out of the PR (5498d5ea); F25 → deferred to #384; F23 (blank condition or target reads as true) → open owner question pending a golden probe; F12/F85 bare `subject.isM2M` read → deferred to the token PRs (scope decision); the description was rewritten and published (addresses F4–F9, F65, F66, F74).
- The orchestrator's recheck of every round-1 finding at this head: `<work>/prev/retest-*.json` and `<work>/axes/previous.json` (findings whose defect remains). Do not re-raise a round-1 finding marked fixed, deferred, or decided unless you show the fix does not hold, is partial (an input of the same class still fails), or introduced a new defect; then cite the round-1 id (e.g. "continues round-1 F14").
- kichasov's review and rechecks: `<work>/raw/reviews.md`, `<work>/raw/issue-comments.md` (items already raised; repeating one without new evidence is not a finding).
- Defect families (round 1 plus this round's fixes): `<work>/families.json`. Orchestrator notes with evidence for the axes: `<work>/orchestrator-notes.md`.

## Behavior norm for the legacy service

- The executable specification in `<executable specification>/` is the norm for legacy behavior: read its `CLAUDE.md` first. Recorded goldens there win over documentation and over model output. The agent answers as its profile `agent`: legacy plus differences, each an owner decision (`<legacy issues list>`, LI-N) or a question.
- The internal OpenAPI specs in <internal API specs, outside the repository> may be read as evidence, never quoted or named in finding text.
- ADRs: `<work>/ws/docs/decisions/` (ADR-0083, 0092, 0093, 0095, 0097–0103 are the contracts this PR implements).

## Repository rules relevant to review (AGENTS.md and .claude/rules at head)

- The Rego in `policies/` holds the caller and token checks that admit every check request (it is reviewed now; the old exemption was removed).
- Complexity: for a fixed policy set, time and memory per request stay linear (up to a sort's log factor) in untrusted bytes from the caller and PIPs; reading a byte once per nesting level or per item of another array breaks that unless a limit keeps it linear. Cost polynomial in policy size. Input too big or too deep fails its request or load, not the process. A count a caller or PIP controls needs a bound at any size.
- Sizing: at most 3 tenants, up to 10000 policies, 1200 permissions per subject, bulk 20–50 items, 5 ms per request. Leave out a cost that appears only beyond these; correctness defects stay in scope.
- Cost-growth tests build only under `//go:build unix && complexity` (`make complexity-tests`).
- Tests: Go `testing` and `testing/synctest`; testify only in test/integration/testify and test/parity/suite; go-cmp only in test/parity/suite.
- Mutation: mutago through `make mutation-diff` with `MUTATION_BASE=<base>`; never `--update-baseline`.
- Commit messages: Conventional Commits, ending with `Assisted-by: <tool> (<model-id>)`, never Co-Authored-By.
- Markdown in the repo wraps at 120 columns.
- A change that adds or renames an option, an error a user can see, or a supported version owes the docs an update.
- Public repository: review text must not name internal products, legacy internal class names, internal documents, or the legacy grammar file. Before writing a finding, check it against: <the repository's grep of internal names>.
- Build and tests: `go test ./...`; `make lint`; `opa` is installed by `bash test/scripts/install-opa.sh` into test/tools/opa/; integration suite on Apple silicon needs `DOCKER_DEFAULT_PLATFORM=linux/arm64`; parity: `go vet -tags integration ./...` and `go test -tags integration -run TestCaseFilesAreWellFormed` in test/parity/suite.

## Scope exclusions

- None stated by the request.

## Reviewers available

- Codex CLI may be usage-limited today; an axis that depends on it and cannot reach it says so in its reply.
