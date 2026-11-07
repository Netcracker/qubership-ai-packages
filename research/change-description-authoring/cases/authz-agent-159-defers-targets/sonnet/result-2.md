Subject for the commit and the title: `feat(token): mark Kubernetes API server providers and check the sub of their tokens`

## 1. Commit message

````text
feat(token): mark Kubernetes API server providers and check the sub of their tokens

The trusted providers file of internal/token/keys cannot mark a provider
as the service account token issuer of a Kubernetes API server, so
nothing in the token packages can tell a Kubernetes token from a
Keycloak one.

A provider now sets kubernetes: true and tokenFile, and may not set
issuer: it takes its issuer from the iss of the token the kubelet writes
into the Pod. Such a provider has to list audiences and may not set
allowMissingAud. verify.Token.Kubernetes() reports the mark of the
provider whose key verified the token, and namespaces.Allowlist.Admit
checks the kubernetes.io.namespace claim of every token of a marked
provider. A Kubernetes token whose sub is not a service account name is
refused, because a marked provider issues only service account tokens.

User-visible changes.
verify.Token.Kubernetes() returns true when the provider whose key verified the token sets kubernetes: true.
A Kubernetes token whose sub does not start with system:serviceaccount is refused with TOKEN_SUBJECT_INVALID and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
Config.Validate refuses a provider without the mark whose id is kubernetes or whose address is an in-cluster name of the API server.

Not changed. The packages are not wired into the service yet, so no
request is handled differently.

ADR-0094 R1 needs the M2M mode, which keys does not read. The change
that wires the packages into the service brings it.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
````

## 2. Pull request title

```text
feat(token): mark Kubernetes API server providers and check the sub of their tokens
```

## 3. Pull request description

````markdown
Before this change, the trusted providers file of `internal/token/keys` cannot mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`, and may not set `issuer`: it takes its issuer from the `iss` of the token the kubelet writes into the Pod. Such a provider has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`. `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

The packages are not wired into the service yet, so no request is handled differently.

**Scope.** This branch is stacked on #202, which sits on #201, and merges after both. #175 is open and also changes `internal/token/namespaces/namespaces.go`; it brings ADR-0094 R20, the agent's own namespace for a topology without a composite. ADR-0092 R7, the M2M rule, comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read, so the change that wires the packages into the service brings it. That change has no pull request or issue yet, so R1 is left out of the trailers.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
````
