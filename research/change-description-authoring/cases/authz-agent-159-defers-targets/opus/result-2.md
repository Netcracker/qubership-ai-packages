## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

The trusted providers file of internal/token/keys had no way to mark a
provider as the service account token issuer of a Kubernetes API
server. Nothing in the token packages could tell a Kubernetes token
from a Keycloak one.

A provider now carries the mark as `kubernetes: true` together with
`tokenFile`. It takes its issuer from the `iss` of the token the
kubelet writes into the Pod, so it sets no `issuer` of its own.
Verification records the mark of the provider whose key verified the
token. A token from a marked provider then has to pass the namespace
allowlist, and its `sub` has to name a service account.

User-visible changes.
`Config.Validate` refuses a provider with `kubernetes: true` that sets `issuer`, sets `allowMissingAud`, or lists no `audiences`.
`Config.Validate` refuses a provider without `kubernetes: true` whose id is `kubernetes` or whose address is an in-cluster name of the API server.
`verify.Token.Kubernetes()` reports whether the provider whose key verified the token has `kubernetes: true`.
`namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token from a provider with `kubernetes: true`.
A `Verifier` without `Admit` refuses every token from a provider with `kubernetes: true` with `TOKEN_NAMESPACE_NOT_ALLOWED`.
A token from a provider with `kubernetes: true` whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

Not changed.
The service handles every request as before: the token packages are not wired into it yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` has no way to mark a provider as the service account token issuer of a Kubernetes API server. Because of that, nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod, so it may not set `issuer`. It also has to list `audiences` and may not set `allowMissingAud`. `Config.Validate` refuses a provider that breaks any of these rules. It also refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token from a marked provider. A `Verifier` without `Admit` refuses every such token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A token from a marked provider whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID`: `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`. The packages are not wired into the service yet, so the service handles every request as before.

**Scope.** This pull request is stacked on #202, which sits on #201, and it merges after both of them. ADR-0094 R20, which covers the agent's own namespace for a topology without a composite, comes with #175. That pull request also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7, the M2M rule, comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read. It waits for the change that wires the packages into the service. That change has no issue yet, so R1 is not on the `Defers:` line.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```
