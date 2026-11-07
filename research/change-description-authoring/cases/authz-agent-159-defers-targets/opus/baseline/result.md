## 1. Commit message

```text
feat(token): mark Kubernetes API server providers and check their tokens

The trusted providers file of internal/token/keys had no way to mark a
provider as the service account token issuer of a Kubernetes API
server. As a result, nothing in the token packages could tell a
Kubernetes token from a Keycloak one.

To mark a provider, set `kubernetes: true` and `tokenFile`. A marked
provider takes its issuer from the `iss` of the token that the kubelet
writes into the Pod, so it may not set `issuer`. It must list
`audiences` and may not set `allowMissingAud`. Config.Validate refuses
an unmarked provider if its id is `kubernetes` or its address is an
in-cluster name of the API server.

verify.Token.Kubernetes() reports the mark of the provider whose key
verified the token. Every token of a marked provider gets two more
checks:

- namespaces.Allowlist.Admit checks its `kubernetes.io.namespace`
  claim. A Verifier without Admit refuses every Kubernetes token with
  TOKEN_NAMESPACE_NOT_ALLOWED.
- If its `sub` does not start with `system:serviceaccount`, the token
  is refused with TOKEN_SUBJECT_INVALID and the message
  `sub "<sub>" names no service account, and provider "<id>" issues
  only service account tokens`.

The service does not use these packages yet, so it handles every
request the same way as before.

Implements: ADR-0091 R6, R8, R10
Implements: ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R1, to the change that wires the token packages into the service
Defers: ADR-0094 R20, to #175
Defers: ADR-0092 R7, to #203
```

## 2. Pull request title

```text
feat(token): mark Kubernetes API server providers and check their tokens
```

## 3. Pull request description

````markdown
A provider in the trusted providers file of `internal/token/keys` can now be marked as the service account token issuer of a Kubernetes API server. Tokens from a marked provider get a namespace check and a `sub` check. Until now, nothing in the token packages could tell a Kubernetes token from a Keycloak one.

**Stacked on #202, which is stacked on #201.** Merge this after both of them.

## Changes

- **Configuration:** to mark a provider, set `kubernetes: true` and `tokenFile`. A marked provider takes its issuer from the `iss` of the token that the kubelet writes into the Pod, so it may not set `issuer`. It must list `audiences` and may not set `allowMissingAud`.
- **Validation:** `Config.Validate` refuses an unmarked provider if its id is `kubernetes` or its address is an in-cluster name of the API server.
- **Verification:** `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
- **Namespace check:** `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token from a marked provider. A `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`.
- **Subject check:** if the `sub` of a Kubernetes token does not start with `system:serviceaccount`, the token is refused with `TOKEN_SUBJECT_INVALID` and this message: `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

The service does not use these packages yet, so it handles every request the same way as before.

## Decision records

Implements: ADR-0091 R6, R8, R10
Implements: ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0094 R1, to the change that wires the token packages into the service
Defers: ADR-0094 R20, to #175
Defers: ADR-0092 R7, to #203

ADR-0094 R1 depends on the M2M mode, which `keys` does not read. The change that wires the packages into the service will bring it. That change has no pull request or issue yet.

Open PR #175 also changes `internal/token/namespaces/namespaces.go`.

## Testing

CI runs `go test ./...` and golangci-lint on every push.
````
