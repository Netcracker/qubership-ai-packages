## 1. Commit message

````text
feat(token): mark Kubernetes providers and check the sub of their tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server, so nothing in the token packages could tell a Kubernetes token
from a Keycloak one.

A provider now sets kubernetes: true and tokenFile. It may not set
issuer, because it takes its issuer from the iss of the token the
kubelet writes into the Pod. verify.Token.Kubernetes() reports the mark
of the provider whose key verified the token, and the namespace and sub
checks below act on that mark.

User-visible changes.
A provider with kubernetes: true must set tokenFile and list audiences, and may not set issuer or allowMissingAud; its issuer is the iss of the token in tokenFile.
Config.Validate refuses a provider without kubernetes: true whose id is kubernetes or whose address is an in-cluster name of the API server.
namespaces.Allowlist.Admit checks the kubernetes.io.namespace claim of every token of a provider marked kubernetes: true.
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
A Kubernetes token whose sub does not start with system:serviceaccount is refused with TOKEN_SUBJECT_INVALID and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

Not changed.
No request is handled differently: the token packages are not wired into the service yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
````

## 2. Pull request title

```text
feat(token): mark Kubernetes providers and check the sub of their tokens
```

## 3. Pull request description

````markdown
The trusted providers file of `internal/token/keys` cannot mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages can therefore tell a Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`. It may not set `issuer`: it takes its issuer from the `iss` of the token the kubelet writes into the Pod. Such a provider has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`. `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.

**Scope.** This pull request is stacked on #202, which sits on #201, and merges after them. No request is handled differently, because the packages it touches are not wired into the service yet.

ADR-0094 R20 (the agent's own namespace for a topology without a composite) comes with #175, which also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7 (the M2M rule) comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read, so the change that wires the packages into the service brings it. That change has no pull request or issue yet, so R1 is in neither trailer.

The repository squashes with the pull request title as the whole message, so whoever merges pastes the two trailer lines below into the body of the squash commit.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
````
