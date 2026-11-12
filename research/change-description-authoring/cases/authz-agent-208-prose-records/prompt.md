# Task

Prepare the pull request below for merging. Give, in Markdown:

1. The full message of the branch's one commit, as it should be when it merges.
2. The pull request title.
3. The pull request description, ready to paste into GitHub.

The facts come from the notes below, which were checked against the code; treat every fact in them as verified, and add
none that they do not carry.

## Repository facts

- Repository: Netcracker/qubership-authz-agent, a Go service that answers authorization checks. Target branch: `main`,
  the default branch. The packages this change touches are not wired into the service yet, so no request is handled
  differently.
- Merge model: the section 4 classifier over the last 40 first-parent commits of `origin/main` prints
  `merge 0 squash 6 plain 34`. `AGENTS.md` says: "Pull requests merge with rebase and merge."
- The history uses Conventional Commits subjects (`feat(token): add …`, `fix(deps): update …`). No release tool reads
  them. There is no pull request template.
- `docs/adr/` holds the architecture decision records, written in prose: each has a Context, a Decision, and
  Consequences, and none numbers its statements. Nothing in the repository asks a pull request to cite them.

## The change

The branch has one commit, `feat(token): give keys that cannot be loaded a reason code of their own`, with no body yet.
It is stacked on #203, which sits on #159, #202, and #201, and merges after them.

Notes from the author:

- Before the change, a token that finds no key gets `TOKEN_KID_UNKNOWN`, whether its source holds no such key or could
  not be asked. An outage of the identity provider therefore reads like a stream of invented tokens.
- `LookupOrReload` now returns `keys.ErrKeysUnavailable` when no loaded key matches and the last load got no answer
  about the keys of the source: the load failed, the wait for it ran out, or a limit refused it. `Verify` turns that
  into the reason code `TOKEN_KEYS_UNAVAILABLE`, with the text
  `the keys of iss "<iss>" cannot be loaded, so the token cannot be checked`.
- A JWKS that lacks the key is an answer, and so is the 404 of a realm that holds no keys. A realm that held keys
  returns 404 only on a failed reload, and its keys stay.
- A 200 response whose `keys` is not an array, `null` included, is a failed load and keeps the keys. `null` used to
  count as an empty array and removed them.
- A token that names a realm that does not exist keeps `TOKEN_KID_UNKNOWN`.
- Seven existing tests changed their expectation from `ErrKeyUnknown` to `ErrKeysUnavailable`, because the limit or the
  wait they exercise is the case this change names. CI runs `go test ./...` and golangci-lint on every push.
- Decisions: ADR-0091 and ADR-0095 give this case a reason code of its own. The change that wires the packages into the
  service has no pull request yet; it brings the rest of ADR-0095, including the reason codes `TOKEN_KIND_NOT_ALLOWED`
  and `CALLER_NOT_M2M`, which depend on the route.
