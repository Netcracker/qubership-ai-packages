# Surface pack: Kubernetes API

Apply this pack when the repository's API *is* the Kubernetes API: it defines CRDs, runs a controller or operator,
serves an admission or conversion webhook, or ships resources a user is expected to author by hand. It does not apply
merely because something runs in a cluster.

A surface pack is a lens, not an axis. Several axes read this file, so **it says who owns what** — stay inside your
row of the table below and leave the rest alone. A concern raised twice in two vocabularies costs the reader more
than it costs you.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Group, kind, plural, shortNames, categories; field naming and casing; `spec` versus `status` split; required versus optional; defaults; enums; printer columns; `kubectl explain` text; subresources; scope (namespaced versus cluster) | `api-ux` |
| Condition `type` vocabulary and polarity; `reason` stability and casing; `message` as the human contract; `observedGeneration`; Events versus conditions; whether a reader can tell "retrying" from "given up" | `error-model` |
| CRD versions, storage version, conversion webhooks; adding a required field; tightening validation over existing objects; changing a default; removing a printer column or a `shortName` | `api-compatibility` |
| Reconcile idempotency and convergence from any intermediate state; finalizers; orphaned external state on delete; requeue and backoff behavior | `correctness` |
| Readiness versus cache sync; metric label cardinality; the on-call drill over real failure modes | `observability-operability` |
| RBAC coverage versus the calls the code actually makes; chart and manifest rendering; CRD lifecycle ownership at install and upgrade | `deployment-config` |

## Normative sources

Fetch these rather than recalling them; the expectation in a finding must cite a section, not a memory.

- **Kubernetes API Conventions** — `kubernetes/community`, `contributors/devel/sig-architecture/api-conventions.md`.
  The authority for naming, optional-versus-required, `spec`/`status`, conditions, and object references.
- **Custom Resource Definition** documentation on `kubernetes.io`, for versioning, conversion, defaulting, pruning,
  and CEL validation rules.
- **The kubebuilder book** for marker semantics, when the project is built with kubebuilder or Operator SDK.
- **`kubectl explain <kind>.<field>`** against the installed CRD: this is the text a user actually reads, and it is
  generated from the Go doc comments. It is both a source and a target of review.

Where the project states its own convention in `AGENTS.md`, `CLAUDE.md`, or a design document, that wins over the
upstream convention — cite the local rule and note the divergence rather than reporting it as a defect.

## `api-ux` — the resource as a hand-authored API

- **Naming.** Kind in `UpperCamelCase`, singular; plural lowercase; group a DNS domain the organization owns. Fields
  `lowerCamelCase`, never `snake_case` or abbreviations a reader must expand. Same concept, same field name across
  every kind in the group — a `classifier` here and a `selector` there for the same thing is the most expensive
  defect on this surface.
- **`spec` versus `status`.** `spec` is the user's desire, `status` is observed reality. Anything in `spec` that the
  controller writes, or anything in `status` the user must fill in, is a defect: it breaks GitOps, which re-applies
  `spec` and will fight the controller.
- **Optionality and defaults.** Every optional field has a documented default and behaves sanely when absent. A field
  marked required that the controller tolerates as empty, or optional that it rejects, is a contract mismatch.
  Booleans that default to `true` cannot be turned off through a merge patch that omits them — flag those.
- **Validation placement.** What is enforced by OpenAPI schema or CEL (`x-kubernetes-validations`), and what is only
  checked by the controller after the object is accepted? The second kind surfaces as a confusing status minutes
  later instead of a rejected `kubectl apply`. List the gaps, and note where CEL genuinely cannot express the rule
  (cross-field rules involving `metadata` are the usual case) — that is a documented limitation, not a defect.
- **Immutability.** Fields whose change would strand external state should say so with a CEL rule. Conversely,
  blanket immutability on everything is its own defect: ask what the day-2 story is for changing the field.
- **Discoverability.** Printer columns that answer "is it healthy, and since when" without `-o yaml`. `shortNames`
  and `categories`. A `status.conditions` subresource. And read the field descriptions as a stranger: a description
  that restates the field name teaches nothing, and it is what `kubectl explain` will show forever.
- **Scope.** A namespaced resource that configures cluster-global behavior lets any namespace owner affect everyone;
  a cluster-scoped resource that only concerns one namespace forces a privileged user into every routine change.
  Report the mismatch here; the architectural question belongs to `architecture`.

## `error-model` — conditions are the contract

- **Condition types** are adjectives describing state, in `UpperCamelCase`, with **positive polarity**: `Ready`,
  `Available`, `Progressing`. `NotReady` is wrong — the polarity lives in `status`, which is `True`, `False`, or
  `Unknown`, and `Unknown` must be reachable and meaningful.
- **`reason`** is the machine contract: `UpperCamelCase`, stable across releases, unique in meaning across the whole
  operator. The same `reason` meaning two different things in two controllers will make an automated consumer act on
  the wrong one. Enumerate every reason the code can emit and check the docs for each; the gap list is the single
  most useful artifact this surface produces.
- **`message`** is the human contract: what happened, what the operator is waiting for, and what the reader should
  do, naming the offending object or field so it can be grepped. Watch for a message that only restates the reason, a
  raw upstream body or Go error dumped verbatim, and a message that changes every reconcile (a timestamp, a UUID) —
  the last one churns `resourceVersion` and defeats diffing for humans and agents alike.
- **`observedGeneration`** on the condition and on `status`: can a reader distinguish "not yet seen" from "seen and
  rejected"? A status describing a generation that was never applied is a defect.
- **Retrying versus given up** is the distinction that decides whether the reader waits or intervenes, and it is the
  one most often missing. Establish how a reader learns which state they are in from `kubectl describe` alone.
- **Events versus conditions.** Events are for transitions a reader would want a timeline of; conditions are for
  current state. An Event per retry floods the namespace; a `Warning` for something the controller is handling
  successfully trains the reader to ignore warnings.

## `api-compatibility` — what a CRD change does to objects already in etcd

Breaking, on this surface, means: existing stored objects stop validating, an apply that worked stops working, or a
consumer reading `status` gets something it cannot parse. Concretely —

- adding a required field, or a CEL rule that existing objects violate;
- narrowing a type, an enum, or a pattern; adding a maximum below values already stored;
- changing a default, which silently changes behavior for every object that omits the field;
- renaming or removing a field, a `shortName`, a printer column, or a condition `reason` a consumer keys on;
- changing the storage version without a conversion webhook, or shipping a conversion that is not round-trip safe.

Check the version machinery itself: is more than one version served, which is `storage: true`, does a conversion
webhook exist and is it tested in both directions? A `v1` shipped without any `v1alpha1`/`v1beta1` history and without
conversion means the first schema mistake is permanent — say so.

Also check CRD lifecycle: who installs and upgrades the CRD, and can an uninstall, a `helm upgrade`, or a disabled
feature flag delete it? Deleting a CRD cascades to every custom resource in the cluster, and from there to anything
those resources own. That is a data-loss path and it is `CRITICAL` wherever it exists.

## `correctness` — reconcile semantics

Idempotency under duplicate delivery; convergence from any state the process can be killed in; finalizers added
before the external effect and removed exactly once; no path where a finalizer can deadlock namespace deletion;
deletion of the CR versus deletion of what it created in the external system, and whether the difference is
documented. Requeue and backoff: is a permanent error retried forever, or a transient one abandoned?

## Tooling

```bash
make manifests generate && git diff --exit-code   # committed CRDs must match the markers
kubectl explain <kind>.spec --recursive           # the text a user actually sees
kubeconform -strict -summary <rendered manifests>
controller-gen crd paths=./api/... output:crd:dir=/tmp/crd-check   # then diff against config/crd/bases
```

Drift between kubebuilder markers and the committed CRDs is itself a finding: it means what ships is not what the
code declares. Where the repository has envtest, a reconcile claim can be executed rather than argued — that is the
cheapest route from `traced` to `executed` on this surface.

**A fake clientset is not an API server, and the difference generates wrong findings in both directions.** The
generated `fake` packages, and hand-rolled fakes, do not evaluate `x-kubernetes-validations` (CEL), do not apply
defaulting or pruning, do not enforce immutability, and take error paths the real typed client does not. Measured on
one review: three axes reported a nil-dereference panic that only the fake can produce, and a verifier refuted a
genuine CEL-immutability defect because its fake-client probe could not see the rejection. So —

- a defect **observed only against a fake** is `PLAUSIBLE` until reproduced against a real API server, envtest, or
  at minimum a `kubectl apply --dry-run=server`;
- a defect **refuted only against a fake** is not refuted at all; say what the fake cannot model and leave the
  finding standing;
- anything about validation, defaulting, immutability, admission, or field pruning must go through a real API
  server. `kubectl apply --dry-run=server` against an installed CRD is usually enough and costs nothing.

## Architectural questions this surface raises

For the `architecture` distiller, not for the evidence axes:

- Is the resource decomposition right — does a working outcome require the user to author two resources whose fields
  must agree by hand?
- Who is the source of truth when the cluster and an external system both hold the state, and what detects drift?
- Is a Kubernetes resource the right shape for an operation that can create but not destroy?
- What is the sharding or ownership model across controller instances, and what makes double-reconciliation
  impossible rather than merely unlikely?
- Does the design survive a GitOps prune, a namespace deletion, and a restore of the external system from backup?
