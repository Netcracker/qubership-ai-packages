## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server. As a result, nothing in the token packages could tell a
Kubernetes token from a Keycloak one.

A provider now marks itself with `kubernetes: true` and names a
`tokenFile`. It takes its issuer from the `iss` of the token that the
kubelet writes into the Pod, so it may not set `issuer`. A marked
provider has to list `audiences` and may not set `allowMissingAud`.
verify.Token.Kubernetes() reports the mark of the provider whose key
verified the token.

Config.Validate also refuses an API server that is configured without
the mark. Without the mark, its tokens would be verified without the
namespace and sub checks that apply to Kubernetes tokens.

User-visible changes.
namespaces.Allowlist.Admit checks the `kubernetes.io.namespace` claim of every token from a provider marked `kubernetes: true`.
A Verifier without Admit refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
Config.Validate refuses a marked provider that sets `issuer` or `allowMissingAud`, or that lists no `audiences`.
Config.Validate refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

Not changed.
The packages are not wired into the service yet, so no request is handled differently.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` could not mark a provider as the service account token issuer of a Kubernetes API server. As a result, nothing in the token packages could tell a Kubernetes token from a Keycloak one.

A provider now marks itself with `kubernetes: true` and names a `tokenFile`. It takes its issuer from the `iss` of the token that the kubelet writes into the Pod, so it may not set `issuer`. It has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token from a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

`Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server. Without the mark, that provider's tokens would be verified without the namespace and `sub` checks. The packages are not wired into the service yet, so no request is handled differently.

**Scope.** This pull request is stacked on #202, which is stacked on #201, and it merges after both. ADR-0094 R20 comes with #175, which is open and also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7 comes with #203, which is also open. ADR-0094 R1 needs the M2M mode, which `keys` does not read, so it waits for the change that wires the packages into the service. That change has no pull request or issue yet. Squash merges here keep only the title, so whoever merges needs to paste the two trailers below into the body of the squash commit.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```
