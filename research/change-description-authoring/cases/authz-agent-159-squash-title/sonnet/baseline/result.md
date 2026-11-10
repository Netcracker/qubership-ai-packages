## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

```markdown
Stacked on #202, which sits on #201. Merge after both.

The trusted providers file of `internal/token/keys` can now mark a provider as the service account token issuer of a Kubernetes API server. Before, nothing in the token packages could tell a Kubernetes token from a Keycloak one. The packages are not wired into the service yet, so no request is handled differently.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 (comes with #175), ADR-0092 R7 (comes with #203), ADR-0094 R1 (comes with the change that wires the packages into the service; no pull request or issue yet)

## Provider configuration

A marked provider sets `kubernetes: true` and `tokenFile`. It may not set `issuer`: it takes its issuer from the `iss` of the token the kubelet writes into the Pod. It has to list `audiences` and may not set `allowMissingAud`.

`Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

## Token checks

- `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
- `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
- A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

## Deferred rules

ADR-0094 R20 (the agent's own namespace for a topology without a composite) comes with #175, an open pull request that also changes `internal/token/namespaces/namespaces.go`. Whichever of the two merges second will need to resolve that file.

ADR-0092 R7 (the M2M rule) comes with #203.

ADR-0094 R1 needs the M2M mode, which `keys` does not read, so the change that wires the packages into the service brings it.

The squash message is the pull request title, with no body.
```
