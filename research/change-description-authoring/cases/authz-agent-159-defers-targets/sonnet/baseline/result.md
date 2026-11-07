## 1. Commit message

```text
feat(token): add Kubernetes API server providers and check their subs

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API server,
so nothing in the token packages could tell a Kubernetes token from a
Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`, and may not set
`issuer`: it takes its issuer from the `iss` of the token the kubelet
writes into the Pod. Such a provider has to list `audiences` and may not
set `allowMissingAud`.

verify.Token.Kubernetes() reports the mark of the provider whose key
verified the token. namespaces.Allowlist.Admit checks the
`kubernetes.io.namespace` claim of every token of a marked provider. A
Verifier without Admit refuses every Kubernetes token with
TOKEN_NAMESPACE_NOT_ALLOWED.

A Kubernetes token whose `sub` does not start with
`system:serviceaccount` is refused with TOKEN_SUBJECT_INVALID and the
text `sub "<sub>" names no service account, and provider "<id>" issues
only service account tokens`.

Config.Validate refuses a provider without the mark whose id is
`kubernetes` or whose address is an in-cluster name of the API server.

The packages are not wired into the service yet, so no request is
handled differently.
```

## 2. Pull request title

```text
feat(token): add Kubernetes API server providers and check their subs
```

## 3. Pull request description

```markdown
Adds a `kubernetes` mark for providers in the trusted providers file of `internal/token/keys`, so the token packages can tell a Kubernetes token from a Keycloak one. The packages are not wired into the service yet, so no request is handled differently.

This pull request is stacked on #202, which sits on #201. Merge it after them. The repository merges with rebase and merge, so the commit message above is what lands in the history.

## What changes

- A provider sets `kubernetes: true` and `tokenFile`, and may not set `issuer`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod. It has to list `audiences` and may not set `allowMissingAud`.
- `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
- `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
- A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
- `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

## Rules

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175, which also changes `internal/token/namespaces/namespaces.go`; ADR-0092 R7 (the M2M rule) to #203; ADR-0094 R1 to the change that wires the packages into the service, because R1 needs the M2M mode and `keys` does not read it. That change has no pull request or issue yet.
```
