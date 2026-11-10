## Title

feat(token): mark the Kubernetes API server as a provider and check the sub of its tokens

## Description

````markdown
## Why

The trusted providers file of `internal/token/keys` cannot say that a provider is the service account token issuer of a Kubernetes API server. `namespaces.Allowlist.Admit` therefore takes a list of provider ids from its caller, and nothing else in the token packages can tell a Kubernetes token from a Keycloak one. The wiring change needs that distinction for the namespace check and for the rule that a Kubernetes token counts as M2M.

ADR-0094 in #160 adds four requirements. A Kubernetes token has to name a service account in `sub`. The provider takes its issuer from a token of the Pod, because #201 requires an `issuer` on every provider and that value differs per cluster. A standard cluster grants discovery only to the group `system:serviceaccounts`, so an anonymous request gets 401 or 403 and the Pod would never become ready. A provider that looks like the API server and has no mark would accept the token of any Pod of the cluster with no namespace check, in every mode.

## What

- **Config.** A provider sets `kubernetes: true` and `tokenFile`, and may not set `issuer`. Without `jwksUri` its keys are found through discovery under that issuer. The form below is for a cluster where discovery does not work:

  ```json
  {"id": "kubernetes",
   "jwksUri": "https://kubernetes.default.svc/openid/v1/jwks",
   "caFile": "/var/run/secrets/tokens/kubernetes/ca.crt",
   "tokenFile": "/var/run/secrets/tokens/kubernetes/token",
   "audiences": ["netcracker"], "kubernetes": true}
  ```

  Such a provider has to list `audiences`: every Pod's default token is issued for the API server itself, and an empty list accepts any `aud`. It may not set `allowMissingAud` either, so a Kubernetes token is accepted only when it names an audience the service accepts.
- **Token.** `verify.Token.Kubernetes()` reports the mark of the provider whose key verified the token.
- **Namespace check.** `namespaces.Allowlist.Admit` is the check itself, a `func(*verify.Token) *verify.Error` that is set as `verify.Options.Admit`. It checks the `kubernetes.io.namespace` claim of every token of a marked provider and passes every other token. A `Verifier` without `Admit` refuses every Kubernetes token, so wiring that leaves the check out refuses these tokens instead of admitting them.
- **Subject.** A Kubernetes token needs a `sub` that starts with `system:serviceaccount`. The rest of `sub` is not parsed, because the namespace comes from the claim above. The check runs after the lifetime, so a token that breaks an earlier rule keeps the code of that rule.
- **Issuer.** `keys.New` takes the `iss` of the token file the kubelet writes in the Pod, without checking the signature, because the file does not come from a caller. `ParseConfig` reads no token. When that issuer is outside the cluster and the provider has no `jwksUri`, the provider sends no token and does not use its `caFile`, because both belong to the cluster. It then trusts the system roots together with `keys.Options.InternalCAFile`, which the wiring sets from `CERTIFICATE_FILE_PATH` when `INTERNAL_TLS_ENABLED` is on, because no other package reads those settings and `keys` reads no environment.
- **Where the token goes.** The token grants access to the API server. A marked provider without `jwksUri` sends it through discovery when the `iss` it read is https on an in-cluster name and `caFile` is set, and a fetch refuses a `jwks_uri` that is not https. A `jwksUri` of a marked provider has to be https on an in-cluster name, or the start stops. An unmarked provider with `tokenFile` needs `jwksUri`.
- **Refusal.** `Config.Validate` refuses a provider without the mark that has the id `kubernetes` or an address on an in-cluster name of the API server, so `ParseConfig` and `New` both fail on it.

Neither a reserved provider id nor the `kubernetes.io` claim decides which tokens are Kubernetes tokens: the id is a label the operator picks, and the claim is whatever the signer puts in the token, while the mark follows the key that verified the token.

## User-visible changes

The packages are not wired into the service, so these outcomes reach only code that calls them.

- A Kubernetes token whose `sub` does not start with `system:serviceaccount` is refused with `TOKEN_SUBJECT_INVALID`: `sub "<sub>" names no service account, and provider "<id>" issues only service account tokens`.
- A `Verifier` without `Admit` refuses a Kubernetes token with `TOKEN_NAMESPACE_NOT_ALLOWED`: `provider "<id>" is a Kubernetes provider and the verifier checks no namespace`.
- `Config.Validate` refuses a marked provider without audiences: `providers[<n>]: provider "<id>" sets kubernetes without audiences; every Pod's default token is issued for the API server, so list the audience this service accepts`.
- `Config.Validate` refuses a marked provider that sets `allowMissingAud`: `providers[<n>]: provider "<id>" sets both kubernetes and allowMissingAud; a Kubernetes token has to name an audience this service accepts`.
- `Config.Validate` refuses an unmarked provider that looks like the API server: `providers[<n>]: provider "<id>" looks like a Kubernetes API server by its id or an address but does not set "kubernetes": true, so the token of any Pod of the cluster would pass with no namespace check; set it on this provider, or give the provider another id if it is not the API server`.
- `Config.Validate` refuses `tokenFile` without `jwksUri` on an unmarked provider: `providers[<n>]: provider "<id>" sets tokenFile without jwksUri; only a provider that sets kubernetes sends a token through discovery, so set jwksUri or remove tokenFile`.
- `Config.Validate` refuses a marked provider that sets `issuer`: `providers[<n>]: provider "<id>" sets both kubernetes and issuer; a provider that sets kubernetes takes its issuer from the token in tokenFile, so remove issuer`.
- `Config.Validate` refuses a marked provider with a `jwksUri` on another host: `providers[<n>]: provider "<id>" sends the token in tokenFile to jwksUri "<uri>", which is outside the cluster, and that token grants access to the API server; set jwksUri to an https address on kubernetes.default.svc or kubernetes.default.svc.cluster.local, or remove jwksUri to find the keys through discovery`.
- `Config.Validate` refuses a marked provider with an http `jwksUri`: `providers[<n>]: provider "<id>" sends the token in tokenFile to jwksUri "<uri>" over http, and that token grants access to the API server; use https`.
- `keys.New` refuses an in-cluster issuer without `caFile` or `jwksUri`: `provider "<id>" takes the in-cluster issuer "<iss>" from tokenFile, and discovery there needs the cluster CA, so set caFile`.
- `keys.New` fails without the token: `provider "<id>" takes its issuer from tokenFile, so mount the token there or fix tokenFile: <cause>`.
- `Config.Validate` refuses a provider without an issuer that does not set `kubernetes` and `tokenFile`: `providers[<n>]: provider "<id>" has no issuer; only a provider that sets kubernetes and tokenFile takes it from its token`.
- `keys.New` logs the issuer it took: `trusted providers: provider "<id>" takes the issuer "<iss>" from <path>`, and for an issuer outside the cluster adds that discovery sends no token and ignores `caFile`.
- A fetch fails on a discovery document that names an http `jwks_uri` for a provider with `tokenFile`: `discovery document <url> names the jwks_uri "<uri>"; provider "<id>" sends its token, so that address has to be https`.

## Verification

`go test ./...` and `go test -race -shuffle=on ./internal/token/...` pass, and golangci-lint is clean.

New tests cover reading the mark, the refused combinations, `Token.Kubernetes()` for two providers that share an id, the refusal without `Admit`, `sub` with and without the prefix, the lifetime checked before `sub`, `IssuerOfTokenFile` on good and malformed files, the refusal of an unmarked provider through `ParseConfig` and `New`, and the token on discovery, on the `jwks_uri`, and against a redirect. The test of `Admit` uses a marked provider named `k8s` and an unmarked one.

Hand mutants of these lines fail the tests. They include dropping each rule above, taking the mark from the id, matching the prefix anywhere in `sub`, checking `sub` before the lifetime, allowing http or no CA on discovery with the token, following a redirect, and keeping or dropping the token and the CA on the wrong side of the in-cluster rule, and each of them on the address of `jwksUri` and the roots of `InternalCAFile`. `TestNew_TrustsTheSystemRootsAndTheInternalCAUnderAnIssuerOutsideTheCluster` compares the pool with the system roots plus the CA, because a test has no public CA to connect through.

## Scope

- This pull request is stacked on #202, which sits on #201, and merges after them.
- The packages are not wired into the service yet, so no request is handled differently.
- The wiring change owes the chart the provider entry, the mount of the projected token, the optional mount of the `topology` ConfigMap, the setting for the JWKS address, and the agent's own namespace. `helm-templates/authz-agent/values.schema.json` and the parser in `components/authz-agent/internal/authn` reject `kubernetes`, as they already reject `caFile` and `tokenFile` of the new format. A documentation page for the new providers file is owed with it.
- #175 also changes `internal/token/namespaces/namespaces.go`. A `topology` file without `composite` allows no namespace here, and #175 changes that to the agent's own namespace, as ADR-0094 decides.
- A standard API server names its own address in `jwks_uri`, not an in-cluster name, so the token follows the address the server names. A run on kind with the wiring checks that this address is reachable from a Pod.
- A count of marked providers needs the M2M mode, which `keys` does not read, so the wiring change brings ADR-0094 R1.

## Rules

```text
Implements: ADR-0091 R6, R8, R10; ADR-0094 R4, R5, R6, R7, R8, R10, R11, R12, R13, R16, R17, R18, R22, R24, R25, R27, R29.
Defers: ADR-0094 R1 to the wiring change; ADR-0094 R20 to #175; ADR-0092 R7 to #203.
```
````
