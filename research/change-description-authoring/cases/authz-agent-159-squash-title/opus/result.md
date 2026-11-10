## 1. Commit message

```text
feat(token): mark Kubernetes providers and check the namespace and sub of their tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server. Nothing in the token packages could tell a Kubernetes token
from a Keycloak one.

A provider now carries the mark with `kubernetes: true` and a
`tokenFile`. It takes its issuer from the `iss` of the token the kubelet
writes into the Pod, so it may not set `issuer`. It has to list
`audiences` and may not set `allowMissingAud`. The namespace and sub
checks below apply only to tokens of a marked provider. For that reason,
Config.Validate refuses a provider that names the API server but does
not carry the mark.

User-visible changes.
verify.Token.Kubernetes() reports whether the provider whose key verified the token carries the `kubernetes` mark.
namespaces.Allowlist.Admit checks the `kubernetes.io.namespace` claim of every token from a provider that carries the mark.
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with TOKEN_SUBJECT_INVALID and `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
Config.Validate refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

Not changed.
The service handles every request as before, because these packages are not wired into it yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```

## 2. Pull request title

```text
feat(token): mark Kubernetes providers and check the namespace and sub of their tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` could not mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages could tell a Kubernetes token from a Keycloak one.

A provider now carries the mark with `kubernetes: true` and a `tokenFile`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod, so it may not set `issuer`. It has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token from a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`. These checks apply only to marked providers. For that reason, `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server. The packages are not wired into the service yet, so the service handles every request as before.

**Scope.** This pull request is stacked on #202, which sits on #201, and merges after both. ADR-0094 R20 (the agent's own namespace for a topology without a composite) comes with #175, which also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7 (the M2M rule) comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read, so it belongs to the change that wires these packages into the service. That change has no issue or pull request yet, so R1 is not in the `Defers:` line. The squash message is only the title, so whoever merges should paste the two trailers below into the body of the squash commit.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```
