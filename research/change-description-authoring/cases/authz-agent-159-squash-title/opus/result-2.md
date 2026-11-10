## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

The trusted providers file of internal/token/keys had no way to mark a
provider as the service account token issuer of a Kubernetes API
server. As a result, nothing in the token packages could tell a
Kubernetes token from a Keycloak one.

A provider now carries the mark itself. A marked provider reads its
issuer from the `iss` of the token that the kubelet writes into the
Pod, so the providers file names the token file instead of the issuer.
The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
A provider with `kubernetes: true` sets `tokenFile` and must list `audiences`; setting `issuer` or `allowMissingAud` on it is refused.
`verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
`namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider.
A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
`Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` has no way to mark a provider as the service account token issuer of a Kubernetes API server. As a result, nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider is now marked with `kubernetes: true` and names a `tokenFile`. It reads its issuer from the `iss` of the token that the kubelet writes into the Pod, so it may not set `issuer`. A marked provider must list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. The mark adds these checks:

- `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
- A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
- `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

The packages are not wired into the service yet, so no request is handled differently.

**Scope.** This pull request is stacked on #202, which is stacked on #201, and merges after both. ADR-0094 R20, the agent's own namespace for a topology without a composite, comes with #175. That pull request also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7, the M2M rule, comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires the packages into the service will bring it, but that change has no issue or pull request yet, so R1 is left out of the trailers below. The squash message is only the title, so whoever merges, please paste the `Implements:` and `Defers:` lines below into the body of the squash commit.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```
