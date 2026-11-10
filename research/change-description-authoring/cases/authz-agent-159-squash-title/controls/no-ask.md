## 1. Commit message

````text
feat(token): mark Kubernetes API server providers and check the namespace and sub of their tokens

The trusted providers file of internal/token/keys had no way to mark a
provider as the service account token issuer of a Kubernetes API
server. As a result, nothing in the token packages could tell a
Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`. It may not set
`issuer`, because it takes its issuer from the `iss` of the token the
kubelet writes into the Pod. A marked provider has to list `audiences`
and may not set `allowMissingAud`. verify.Token.Kubernetes() reports
the mark of the provider whose key verified the token.
namespaces.Allowlist.Admit checks the `kubernetes.io.namespace` claim
of every token of a marked provider.

User-visible changes.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with TOKEN_SUBJECT_INVALID and `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
Config.Validate refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

Not changed.
The packages are not wired into the service yet, so no request is handled differently.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
````

## 2. Pull request title

```text
feat(token): mark Kubernetes API server providers and check the namespace and sub of their tokens
```

## 3. Pull request description

````markdown
The trusted providers file of `internal/token/keys` cannot mark a provider as the service account token issuer of a Kubernetes API server. As a result, nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`. It may not set `issuer`, because it takes its issuer from the `iss` of the token the kubelet writes into the Pod. A marked provider has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and this text:

```text
sub "<sub>" names no service account, and provider "<id>" issues only service account tokens
```

`Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server. The packages are not wired into the service yet, so no request is handled differently.

**Scope.** This pull request is stacked on #202, which sits on #201, and merges after both. #175 brings ADR-0094 R20, the agent's own namespace for a topology without a composite. It also changes `internal/token/namespaces/namespaces.go`, so the two pull requests overlap on that file. #203 brings ADR-0092 R7, the M2M rule. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires the packages into the service will bring it, but that change has no pull request or issue yet, so the trailers leave R1 out. The squash keeps only the title, so the two trailers below never reach the history.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
````
