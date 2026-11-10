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
- `docs/decisions/` holds the architecture decision records. Records from ADR-0091 on number their rules (`R1`, `R2`,
  …), and `docs/decisions/README.md` says: "A pull request that changes code under a record says which rules it covers,
  as `Implements:` and `Defers:` lines."

## The change

The branch has one commit, `feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens`,
with no body yet. It is stacked on #202, which sits on #201, and merges after them.

Notes from the author:

- Before the change, the trusted providers file of `internal/token/keys` cannot mark a provider as the service account
  token issuer of a Kubernetes API server, so nothing in the token packages can tell a Kubernetes token from a Keycloak
  one.
- A provider now sets `kubernetes: true` and `tokenFile`, and may not set `issuer`: it takes its issuer from the `iss`
  of the token the kubelet writes into the Pod. Such a provider has to list `audiences` and may not set
  `allowMissingAud`.
- `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
  `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a
  `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
- A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID`
  and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
- `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name
  of the API server.
- CI runs `go test ./...` and golangci-lint on every push.
- Rules: the change brings ADR-0091 R6, R8, and R10, and ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17,
  R18, R22, R24, R25, R27, and R29.
- ADR-0094 R20, the agent's own namespace for a topology without a composite, comes with #175, an open pull request
  that also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7, the M2M rule, comes with #203, an open pull
  request. ADR-0094 R1 needs the M2M mode, which `keys` does not read, so the change that wires the packages into the
  service brings it; that change has no pull request and no issue yet.
