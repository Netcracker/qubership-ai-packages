## 1. Commit message

```text
feat(token): mark a provider as a Kubernetes API server and check its tokens

The trusted providers file of internal/token/keys can mark a provider
as the service account token issuer of a Kubernetes API server. Before
this change, nothing in the token packages could tell a Kubernetes
token from a Keycloak one.

A marked provider sets `kubernetes: true` and `tokenFile`. It takes its
issuer from the `iss` of the token the kubelet writes into the Pod, so
it may not set `issuer`. It has to list `audiences` and may not set
`allowMissingAud`.

verify.Token.Kubernetes() reports the mark of the provider whose key
verified the token. namespaces.Allowlist.Admit checks the
kubernetes.io.namespace claim of every token of a marked provider. A
Verifier without Admit refuses every Kubernetes token with
TOKEN_NAMESPACE_NOT_ALLOWED. A Kubernetes token whose sub does not
start with system:serviceaccount is refused with TOKEN_SUBJECT_INVALID.

Config.Validate refuses an unmarked provider whose id is `kubernetes`
or whose address is an in-cluster name of the API server.

The packages are not wired into the service yet, so no request is
handled differently.
```

## 2. Pull request title

```text
feat(token): mark a provider as a Kubernetes API server and check its tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` can now mark a provider as the service account token issuer of a Kubernetes API server. Before this change, nothing in the token packages could tell a Kubernetes token from a Keycloak one.

The packages are not wired into the service yet, so no request is handled differently.

This pull request is stacked on #202, which is stacked on #201. Merge it after both.

## Changes

- A marked provider sets `kubernetes: true` and `tokenFile`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod, so it may not set `issuer`. It has to list `audiences` and may not set `allowMissingAud`.
- `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
- `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
- A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
- `Config.Validate` refuses an unmarked provider whose id is `kubernetes` or whose address is an in-cluster name of the API server.

## Rules

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175
Defers: ADR-0092 R7 to #203
Defers: ADR-0094 R1 to the change that wires the packages into the service, which has no pull request or issue yet

ADR-0094 R20 covers the agent's own namespace for a topology without a composite. #175 also changes `internal/token/namespaces/namespaces.go`, so whichever of the two pull requests merges second has to be rebased onto the other.

ADR-0092 R7 is the M2M rule. ADR-0094 R1 needs the M2M mode, and `keys` does not read that mode.
```
