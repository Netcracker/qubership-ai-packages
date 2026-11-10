## 1. Commit message

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

Before this change, the trusted providers file of internal/token/keys
cannot mark a provider as the service account token issuer of a
Kubernetes API server, so nothing in the token packages can tell a
Kubernetes token from a Keycloak one.

A provider now carries the mark, and a verified token reports the mark
of the provider whose key verified it. The sub and namespace checks
apply to the tokens of marked providers. A marked provider takes its
issuer from the iss of the token the kubelet writes into the Pod, so
the file does not name it.

ADR-0094 R1 needs the M2M mode, which keys does not read. The change
that wires these packages into the service brings it.

**User-visible changes.**
Config.Validate refuses a provider without `kubernetes: true` whose id is `kubernetes` or whose address is an in-cluster name of the API server. Both were accepted before.
A provider with `kubernetes: true` sets `tokenFile` and takes its issuer from the `iss` of the token in that file; it must not set `issuer`, must list `audiences`, and must not set `allowMissingAud`.
verify.Token.Kubernetes() reports the mark of the provider whose key verified the token.
namespaces.Allowlist.Admit checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a Verifier without Admit refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

**Not changed.**
The service handles every request as before, because the packages this change touches are not wired into it yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
```

## 2. Pull request title

```text
feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens
```

## 3. Pull request description

**Breaking changes.** `Config.Validate` now refuses a provider without `kubernetes: true` whose id is `kubernetes` or whose address is an in-cluster name of the API server. It accepted both before. Mark such a provider with `kubernetes: true`, or change its id and address. The service does not call `Config.Validate` on these packages yet, so no deployed configuration is affected.

Before this change, the trusted providers file of `internal/token/keys` cannot mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider sets `kubernetes: true` and `tokenFile`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod, so it may not set `issuer`. It must list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`. No request is handled differently, because the packages are not wired into the service.

**Scope.** This branch is stacked on #202, which sits on #201, and merges after both. Open PR #175 also changes `internal/token/namespaces/namespaces.go` and brings ADR-0094 R20, the agent's own namespace for a topology without a composite. Open PR #203 brings ADR-0092 R7, the M2M rule. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires the packages into the service brings it, and that change has no pull request or issue yet.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R20 to #175; ADR-0092 R7 to #203
