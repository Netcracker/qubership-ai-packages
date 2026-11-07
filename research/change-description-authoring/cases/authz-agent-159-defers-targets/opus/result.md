## 1. Commit message

```text
feat(token): mark Kubernetes API server providers and check their tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server. As a result, nothing in the token packages could tell a
Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`, and may not set
`issuer`. Its issuer is the `iss` of the token that the kubelet writes
into the Pod. A marked provider has to list `audiences` and may not set
`allowMissingAud`. verify.Token.Kubernetes() reports the mark of the
provider whose key verified the token. namespaces.Allowlist.Admit
checks the `kubernetes.io.namespace` claim of every token of a marked
provider.

The namespace and sub checks apply only to tokens of marked providers.
Config.Validate therefore refuses an unmarked provider that looks like
the API server, because such a provider would skip both checks.

User-visible changes.
A marked provider that sets `issuer` or `allowMissingAud`, or lists no `audiences`, is refused.
Config.Validate refuses a provider without `kubernetes: true` whose id is `kubernetes` or whose address is an in-cluster name of the API server.
A Verifier without Admit refuses every token of a marked provider with TOKEN_NAMESPACE_NOT_ALLOWED.
A token of a marked provider whose `sub` does not start with `system:serviceaccount` is refused with TOKEN_SUBJECT_INVALID and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

Not changed.
The service does not use these packages yet, so it handles every request as before.

ADR-0094 R1 needs the M2M mode, which keys does not read. The change
that wires these packages into the service brings that rule.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```

## 2. Pull request title

```text
feat(token): mark Kubernetes API server providers and check the namespace and sub of their tokens
```

## 3. Pull request description

```markdown
The trusted providers file of `internal/token/keys` has no way to mark a provider as the service account token issuer of a Kubernetes API server. As a result, nothing in the token packages can tell a Kubernetes token from a Keycloak one.

A provider now sets `kubernetes: true` and `tokenFile`, and may not set `issuer`. Its issuer is the `iss` of the token that the kubelet writes into the Pod. A marked provider has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every such token with `TOKEN_NAMESPACE_NOT_ALLOWED`.

A token of a marked provider whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and this text:

```text
sub "<sub>" names no service account, and provider "<id>" issues only service account tokens
```

The namespace and sub checks apply only to tokens of marked providers. For that reason, `Config.Validate` refuses a provider without the mark whose id is `kubernetes` or whose address is an in-cluster name of the API server, because such a provider would skip both checks.

**Scope.** This branch is stacked on #202, which sits on #201, and it merges after both. The service does not use these packages yet, so it handles every request as before. ADR-0094 R20, the agent's own namespace for a topology without a composite, comes with #175. That pull request also changes `internal/token/namespaces/namespaces.go`, so the two overlap in that file. ADR-0092 R7, the M2M rule, comes with #203. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires these packages into the service will bring it, but that change has no pull request or issue yet, so R1 is not on the `Defers:` line.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```
