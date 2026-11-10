## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check its tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server. Nothing in the token packages could tell a Kubernetes token
from a Keycloak one, so nothing could apply rules that only Kubernetes
tokens need.

A provider now sets kubernetes: true and tokenFile. It may not set
issuer: it takes its issuer from the iss of the token the kubelet
writes into the Pod. It has to list audiences and may not set
allowMissingAud. verify.Token.Kubernetes() reports the mark of the
provider whose key verified the token, and namespaces.Allowlist.Admit
checks the kubernetes.io.namespace claim of every token of a marked
provider. A Verifier without Admit refuses every Kubernetes token, so a
missing namespace check cannot let one through. Config.Validate also
refuses an unmarked provider that names the API server, so the mark
cannot be left off by accident.

User-visible changes.
Config.Validate refuses a provider without kubernetes: true whose id is "kubernetes" or whose address is an in-cluster name of the API server, so a trusted providers file that lists one fails validation until the provider is marked.
verify.Token.Kubernetes() returns the mark of the provider whose key verified the token.
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
A Kubernetes token whose sub does not start with system:serviceaccount is refused with TOKEN_SUBJECT_INVALID and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

Not changed.
The packages are not wired into the service yet, so no request is handled differently.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check its tokens
```

## 3. Pull request description

**Breaking changes.** `Config.Validate` now refuses a provider without `kubernetes: true` whose id is `kubernetes` or whose address is an in-cluster name of the API server. A trusted providers file that lists one fails validation until the provider is marked. The packages are not wired into the service yet, so no deployed configuration is affected.

The trusted providers file of `internal/token/keys` could not mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages could tell a Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`, and takes its issuer from the `iss` of the token the kubelet writes into the Pod. Such a provider may not set `issuer` or `allowMissingAud`, and has to list `audiences`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`, so a missing namespace check cannot let one through. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

**Scope.** This branch is stacked on #202, which sits on #201, and merges after them. #175 also changes `internal/token/namespaces/namespaces.go`, and neither pull request depends on the other. ADR-0094 R20 (the agent's own namespace for a topology without a composite) comes with #175, and ADR-0092 R7 (the M2M rule) comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires the packages into the service brings it, and that change has no pull request or issue yet, so R1 is not in `Defers`.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
