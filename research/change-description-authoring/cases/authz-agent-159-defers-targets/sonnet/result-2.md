```text
feat(token): mark Kubernetes providers and check the namespace and sub of their tokens

The trusted providers file of internal/token/keys could not mark a
provider as the service account token issuer of a Kubernetes API
server, so nothing in the token packages could tell a Kubernetes token
from a Keycloak one, and no check could apply to Kubernetes tokens
alone.

A provider now sets "kubernetes: true" and "tokenFile". It may not set
"issuer" and takes its issuer from the "iss" of the token the kubelet
writes into the Pod. It has to list "audiences" and may not set
"allowMissingAud". verify.Token.Kubernetes() reports the mark of the
provider whose key verified the token, and the namespace and subject
checks key off it. Config.Validate refuses an unmarked provider that
looks like the API server, so that its tokens cannot skip those checks.
The packages are not wired into the service yet, so no request is
handled differently.

User-visible changes.
A provider with "kubernetes: true" and "tokenFile" and no "issuer" takes its issuer from the "iss" of the token the kubelet writes into the Pod.
A provider with "kubernetes: true" that sets "issuer", sets "allowMissingAud", or lists no "audiences" is refused when the file is validated.
Config.Validate refuses a provider without "kubernetes: true" whose id is "kubernetes" or whose address is an in-cluster name of the API server. Such a file validated before.
verify.Token.Kubernetes() reports true when the provider whose key verified the token carries the mark.
namespaces.Allowlist.Admit checks the "kubernetes.io.namespace" claim of every token of a marked provider.
A Verifier without Admit refuses every Kubernetes token with TOKEN_NAMESPACE_NOT_ALLOWED.
A Kubernetes token whose "sub" does not start with "system:serviceaccount" is refused with TOKEN_SUBJECT_INVALID and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```

# Pull request title

```text
feat(token): mark Kubernetes providers and check the namespace and sub of their tokens
```

# Pull request description

```markdown
**Breaking changes.** A trusted providers file that `Config.Validate` accepted before is now refused when a provider without `kubernetes: true` has the id `kubernetes` or an in-cluster name of the API server as its address. To fix the file, set `kubernetes: true` with `tokenFile` and `audiences` on that provider, or change its id and address if it is not the API server.

The trusted providers file of `internal/token/keys` could not mark a provider as the service account token issuer of a Kubernetes API server. Nothing in the token packages could tell a Kubernetes token from a Keycloak one, so no check could apply to Kubernetes tokens alone.

A provider now sets `kubernetes: true` and `tokenFile`. It takes its issuer from the `iss` of the token the kubelet writes into the Pod, so it may not set `issuer`. It has to list `audiences` and may not set `allowMissingAud`. `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token. `namespaces.Allowlist.Admit` checks the `kubernetes.io.namespace` claim of every token of a marked provider, and a `Verifier` without `Admit` refuses every Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`. A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID` and the text `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`. The `Config.Validate` refusal above exists so that a provider for the API server cannot go unmarked and skip these two checks.

The packages are not wired into the service yet, so no request is handled differently.

**Scope.** This pull request is stacked on #202, which sits on #201, and merges after them. #175 is open and also changes `internal/token/namespaces/namespaces.go`, and it brings ADR-0094 R20, the agent's own namespace for a topology without a composite. #203 is open and brings ADR-0092 R7, the M2M rule. ADR-0094 R1 needs the M2M mode, which `keys` does not read. The change that wires the packages into the service brings it, and that change has no pull request and no issue yet, so R1 is not in the trailers.

Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29
Defers: ADR-0092 R7 to #203; ADR-0094 R20 to #175
```
