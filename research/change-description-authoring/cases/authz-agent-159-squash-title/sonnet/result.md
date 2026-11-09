## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server, so nothing in the token packages could tell a Kubernetes token
from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`, and takes its
issuer from the `iss` of the token the kubelet writes into the Pod, so
it may not set `issuer`. Such a provider has to list `audiences`.
verify.Token.Kubernetes() reports the mark of the provider whose key
verified the token, and namespaces.Allowlist.Admit uses it to check the
namespace of every Kubernetes token.

User-visible changes.
A provider with `kubernetes: true` and `tokenFile` loads, and its issuer is the `iss` of the token the kubelet writes into the Pod.
Config.Validate refuses a provider with `kubernetes: true` that sets `issuer`, that omits `audiences`, or that sets `allowMissingAud`.
Config.Validate refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server.
verify.Token.Kubernetes() returns the mark of the provider whose key verified the token.
namespaces.Allowlist.Admit checks the `kubernetes.io.namespace` claim of every token of a marked provider.
A Verifier without Admit refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

Not changed.
The service handles every request as before: the token packages are not wired into it yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

Before this change, the trusted providers file of `internal/token/keys` could not mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages could tell a Kubernetes token from a Keycloak one, so the namespace and subject checks had nothing to attach to.

A provider now sets `kubernetes: true` and `tokenFile`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod, so it may not set `issuer`. It has to list `audiences` and may not set `allowMissingAud`. `Config.Validate` also refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

**Scope.** This pull request is stacked on #202, which sits on #201, and merges after them. The packages it touches are not wired into the service, so no request is handled differently.

ADR-0094 R20 (the agent's own namespace for a topology without a composite) comes with #175, which also changes `internal/token/namespaces/namespaces.go`. ADR-0092 R7 (the M2M rule) comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read, so the change that wires the packages into the service brings it. That change has no pull request or issue yet, so R1 is not in the trailers below.

The squash message is the pull request title alone, so whoever merges: please paste the two trailer lines below into the body of the squash commit.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
