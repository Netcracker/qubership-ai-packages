## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

The trusted providers file of internal/token/keys had no way to mark a
provider as the service account token issuer of a Kubernetes API
server. As a result, nothing in the token packages could tell a
Kubernetes token from a Keycloak one.

A provider is now marked with `kubernetes: true` and sets `tokenFile`.
Its issuer comes from the `iss` of the token that the kubelet writes
into the Pod, so the provider does not set `issuer` itself.
verify.Token.Kubernetes() reports the mark of the provider whose key
verified the token. namespaces.Allowlist.Admit checks the
`kubernetes.io.namespace` claim of every token from a marked provider.

User-visible changes.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with TOKEN_SUBJECT_INVALID: `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
Config.Validate refuses a provider marked `kubernetes: true` that sets `issuer` or `allowMissingAud`, or that lists no `audiences`.
Config.Validate refuses an unmarked provider whose id is `kubernetes` or whose address is an in-cluster name of the API server.

Not changed.
The service handles every request as before, because these packages are not wired into it yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` can't mark a provider as the service account token issuer of a Kubernetes API server. As a result, nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider is now marked with `kubernetes: true` and sets `tokenFile`. Its issuer comes from the `iss` of the token that the kubelet writes into the Pod. `Config.Validate` refuses a marked provider that sets `issuer` or `allowMissingAud`, or that lists no `audiences`. It also refuses an unmarked provider whose id is `kubernetes` or whose address is an in-cluster name of the API server. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token from a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

These packages are not wired into the service yet, so the service handles every request as before.

**Scope.** This pull request is stacked on #202, which sits on #201, and merges after both. ADR-0094 R20 (the agent's own namespace for a topology without a composite) comes with #175. That pull request is still open and also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7 (the M2M rule) comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires the packages into the service will bring R1, but that change has no issue or pull request yet, so R1 is not on the `Defers:` line.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```
