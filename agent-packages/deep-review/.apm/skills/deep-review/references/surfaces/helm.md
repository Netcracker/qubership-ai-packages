# Surface pack: Helm chart

Apply this pack when the repository ships a Helm chart that somebody else installs: a chart directory with a
`Chart.yaml`, published or vendored, with `values.yaml` as the knob a user turns. It does not apply to a chart that
exists only to stand the project up in its own CI — that is test scaffolding, and reviewing it as an API produces
findings nobody will act on.

The chart's API is **the values contract**, not the templates. Templates are an implementation the maintainer may
rewrite; a value name that shipped is a promise to every release already running. Keep that distinction in front of you
— most weak findings on this surface are template taste dressed up as a defect.

A repository often carries this pack alongside another. An operator has `kubernetes` (the CRD it serves) *and* `helm`
(the chart that installs it), and the two disagree about naming — `lowerCamelCase` fields in a CRD, `lowerCamelCase`
values in a chart, but `UPPER_SNAKE_CASE` values where a platform contract mandates it. Read both packs and do not
carry a rule across.

A surface pack is a lens, not an axis. Several axes read this file, so **it says who owns what** — stay inside your
row of the table below and leave the rest alone. A concern raised twice in two vocabularies costs the reader more
than it costs you.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Value naming and casing; flat versus nested; what belongs under `global`; defaults that install unattended; documentation of each value; `values.schema.json` coverage; `NOTES.txt`; `--set` ergonomics | `api-ux` |
| Renaming, removing, or moving a value; changing a default; tightening the schema; subchart `alias` and `condition` keys; chart `version` / `appVersion` discipline; rendered object names and immutable fields; CRD install-and-upgrade ownership | `api-compatibility` |
| Rendering the matrix of profiles and toggles; probes, resources, RBAC, scheduling; hooks; the install / upgrade / rollback / uninstall drill | `deployment-config` |
| Template logic: falsy defaults, type coercion, indentation shape, non-determinism, `lookup`, checksum annotations, subchart value plumbing that silently does nothing | `correctness` |
| What a user sees when a value is wrong, and where they see it: `required` and `fail` messages, schema violation text, render error versus apply error versus a pod that crash-loops an hour later | `error-model` |
| Secrets in values and in rendered output; image pinning; pod security context; RBAC breadth; supply chain of the dependencies | `security` |
| `helm unittest` and golden renders; `ct lint` / `ct install`; `kubeconform` across the declared `kubeVersion` range | `tests` |
| PVC retention, `helm.sh/resource-policy`, what an uninstall deletes | `data-lifecycle` |
| Packaging, `Chart.lock`, OCI publishing, provenance, generated README drift | `build-release`, `docs-onboarding` |

## Normative sources

Fetch these rather than recalling them; the expectation in a finding must cite a section, not a memory.

- **Helm Chart Best Practices** on `helm.sh/docs/chart_best_practices/` — conventions, values, templates,
  dependencies, labels and annotations, pods, custom resource definitions, RBAC. The authority for naming and
  structure.
- **Chart.yaml and chart structure** documentation for `version` / `appVersion` / `kubeVersion` / `dependencies`
  semantics, and for what `crds/` does and does not do.
- **JSON Schema** (the draft the chart's `values.schema.json` declares) for what the schema can and cannot express.
- **Kubernetes recommended labels** (`app.kubernetes.io/*`) for the label set the rendered objects carry.
- **The Helm release notes for the major version in use.** Helm 4 changed the apply path to server-side apply,
  switched readiness to `kstatus`, and tightened chart validation, so a chart that linted clean under v3 can fail
  under v4, and a release created by v3 keeps client-side apply until it is migrated. Check `helm version` first and
  say which one your findings are against.

Where the project states its own convention in `AGENTS.md`, `CLAUDE.md`, a platform contract document, or a
`values.schema.json` annotation, that wins over the upstream convention — cite the local rule and note the divergence
rather than reporting it as a defect.

## `api-ux` — values as a hand-authored API

- **Naming.** `lowerCamelCase`, beginning with a lowercase letter — uppercase is reserved for Helm's own built-ins —
  and no hyphens, which cannot be reached by `.Values.my-value` without `index`. One concept, one name across every
  subchart: `enabled` here and `install` there for the same switch is the most expensive defect on this surface,
  because it is the one users hit on every chart they touch.
- **Flat versus nested.** Nest a group the user sets as a unit; never nest a lone scalar. Every level of nesting is a
  level of existence checking in the templates and a longer `--set` path for the user. A knob that documentation tells
  people to override on the command line does not belong five levels down, and never inside a list — list elements
  cannot be addressed by `--set` in any way a user will remember.
- **Merge semantics are part of the contract, and they surprise people.** Maps merge key by key; **lists replace
  wholesale**, so a user who wants to add one entry to a default list must restate all of it, and adding a default
  entry later will not reach them. A `null` in an override deletes the key rather than resetting it to the default.
  Where a list-valued knob is meant to be extended, say so, or offer an `extra*` sibling.
- **Defaults must install unattended.** `helm install <name> <chart>` with no flags is the acceptance test. Render it,
  then read what came out: a default that renders but cannot schedule, pulls an image that does not exist, or requires
  a secret nobody created, is a defect at the same severity as a template that fails to render.
- **Every value documented where the user reads it.** A comment in `values.yaml`, a `description` in the schema, and a
  README table are three surfaces that drift apart; check the generated one (`helm-docs`) against the source rather
  than assuming CI regenerates it.
- **`values.schema.json`.** Does it exist, and does it cover the values that actually matter — types, enums, required
  combinations — or only the ones that were easy? A schema is the cheapest place to turn a confusing runtime failure
  into a rejected `helm install`. `additionalProperties: false` is attractive and dangerous: with subcharts, `global`,
  and platform-injected values it rejects things the user is entitled to pass. Report its absence *and* its overreach.
- **`global`.** A key under `global` that only one subchart reads is misplaced, and a subchart that reads a parent
  value not declared anywhere is a coupling nobody can discover. Enumerate what crosses the boundary in each
  direction.
- **`NOTES.txt`** tells the operator what to do next — the URL, the command, the credential lookup. Check that it does
  not print a secret, and that it says something true when the values differ from the defaults.

## `api-compatibility` — what a chart change does to a release already running

Breaking, on this surface, means: a `values.yaml` or `--set` line that worked stops working, or keeps working and
silently means something else. Concretely —

- renaming or removing a value; moving it into or out of `global`; renaming a subchart or changing its `alias`, which
  moves every value under it; changing a dependency `condition` key, which turns a component off without a message;
- **changing a default** — the highest-frequency real defect here, because it reaches every release that omits the
  value and leaves no trace in anybody's `values.yaml`;
- tightening the schema: a new `required`, a narrower `enum` or `pattern`, or `additionalProperties: false` rejects
  values that were previously accepted, and the rejection lands at *upgrade* of a running release, not at install;
- changing what the templates *name*. `spec.selector` on a Deployment, and `selector`, `serviceName`, and
  `volumeClaimTemplates` on a StatefulSet, are immutable: a change to the fullname helper or to the selector labels
  makes `helm upgrade` fail on an existing release, and in the worse variant renames the object so the old one is
  orphaned and keeps serving. Service `clusterIP` and type transitions, Job pod templates, PVC shrinking, and an
  immutable ConfigMap or Secret behave the same way. Diff the rendered output between the previous release tag and
  `HEAD` — this is the one command that settles the whole question, and it is cheap.

### When the project states a compatibility window

Some organizations promise more than semver: *a values file that worked N years ago still installs today.* Where such
a policy exists — in `AGENTS.md`, a platform contract, or a release policy — it is the expectation source, and it
changes the question this axis answers. You are no longer arguing about whether a change is breaking; you are
measuring whether an old input still works, which is executable and therefore worth doing over any amount of reading.

```bash
git log --diff-filter=A --format='%h %ad' --date=short -- <chart>/values.yaml   # how far back the chart goes
git show <ref-from-N-years-ago>:<chart>/values.yaml > work/values-old.yaml
helm template rel <chart> -f work/values-old.yaml                               # must render
helm install rel <chart> -f work/values-old.yaml --dry-run=server               # must be accepted
```

Take the inputs from the oldest supported release: the `values.yaml` of the day, the examples in that release's
README, and any documented `--set` lines. Render each one against `HEAD`. A failure is a finding at the severity of a
broken promise; a render that succeeds but produces different objects is a separate, quieter finding — the policy
usually guarantees that the chart *installs*, not that behavior is unchanged, so say which of the two you measured and
which the policy covers.

Under such a policy two ordinary practices become defects on sight, and both are cheap to check:

- **A new parameter without a working default**, or a new `required` in the schema or a `required` call in a template.
  Any input from the window omits it, so the promise breaks the moment it ships.
- **A removal or rename with no compatibility shim.** The old key must still be read, mapped to the new one, and
  ideally warned about, with the precedence when both are set documented *and* tested — a rename with an alias that
  nobody rendered with both keys set is the version of this fix that silently drops the old value.

Schema tightening deserves its own look here: a new `enum`, `pattern`, `minimum`, or `additionalProperties: false`
rejects yesterday's file without anyone touching a template. And note the boundary, because it is where reviews of
this kind go wrong: a parameter-compatibility promise says nothing about the CRDs the chart installs or the persisted
state it owns. Those are separate contracts with separate failure modes — see the CRD paragraph above and the
`data-lifecycle` axis, and do not let the policy be cited as cover for either.

Check the version machinery itself: does `version` move on every chart change, is `appVersion` the application's, and
does anything state whether the values surface is under semver at all? Then check the dependencies: a floating range
(`~0`, `*`, a branch) means a subchart's values contract can change with no commit in this repository, which is a
supply-chain fact and a compatibility fact at once. Say whether `Chart.lock` exists and whether it is current.

**CRD lifecycle is the data-loss path on this surface, and it is `CRITICAL` wherever it exists.** Establish which
mechanism the chart uses. Files in `crds/` are installed once and are never upgraded, never deleted, and never
templated — so a schema change ships to new clusters only, and the upgrade path has to be documented or it does not
exist. A CRD rendered from `templates/` instead is upgraded, and is also **deleted on uninstall, cascading to every
custom resource in the cluster and to everything those resources own**. A chart that does both, or a separate CRD
chart whose ownership at `helm upgrade` is not stated, is worth tracing end to end.

A project may take CRDs out of Helm's hands entirely — a dedicated CRD chart applied with `kubectl apply
--server-side` and the workload chart installed with `--skip-crds`. That is a legitimate answer to everything above,
and where the repository documents it, it is the local convention and it wins. The review then asks two narrower
questions instead: does anything under `templates/` still render a CRD and quietly reintroduce the delete cascade,
and does the documented sequence actually work — install the CRDs, install the chart, upgrade both, in that order,
against a cluster.

## `deployment-config` — rendering and the lifecycle

The axis file has the general questions. On this surface, add:

- **Render the matrix, not the default.** Default values; each shipped profile or preset; each component toggle in
  both positions, including the combinations the conditions allow but nobody tried; the lowest and highest Kubernetes
  version `kubeVersion` claims. A template that renders under one toggle and fails under another is the common case,
  and reading will not find it.
- **Hooks.** Weights and ordering; `hook-delete-policy`; whether a `pre-upgrade` Job is idempotent, since it runs
  again on every retry; `backoffLimit` and `ttlSecondsAfterFinished`, without which failed hook Jobs accumulate in the
  namespace. And the rule that catches people: **hooks are not rolled back.** `helm rollback` reverts the tracked
  objects, does not re-run the upgrade hooks, and does not undo whatever they did to a database.
- **`helm.sh/resource-policy: keep`** on anything that must survive an uninstall — and the mirror defect, a kept
  resource that then blocks a clean reinstall with an ownership conflict.
- **RBAC the chart grants against the calls the code makes.** Check in that direction; grants checked against
  themselves always look complete. Where a switch claims to drop to namespace scope, render it and confirm no
  `ClusterRole` or `ClusterRoleBinding` survives.
- **`.Capabilities` and `kubeVersion`.** A template that branches on `.Capabilities.APIVersions` renders differently
  against a cluster than under `helm template`, which fakes them. Any finding about such a branch needs a real render
  target or an explicit `--kube-version` / `--api-versions`, and must say which.

## `correctness` — template logic

- **`default` swallows every falsy value.** `.Values.x | default true` cannot be set to `false`, `| default 30` cannot
  be set to `0`, and `| default "info"` cannot be set to `""`. `coalesce` and `empty` share the flaw. The correct test
  for "the user did not set it" is `hasKey` or `kindIs "invalid"`. This is the single most common real defect in Helm
  templates and it is trivially demonstrable: render with the value set to `false` and show that it did not take.
- **Types and quoting.** YAML will read `on`, `yes`, `01`, and `1.0` as something other than the string the user
  typed, and a percentage such as `25%` must stay quoted or it is not valid where an `IntOrString` is expected.
  Conversely a numeric knob rendered through `quote` arrives as a string and is rejected by the API server. Render and
  inspect the type, do not reason about it.
- **Indentation is structure.** `indent` where `nindent` was meant, or a chomped `{{-`, produces YAML that parses
  cleanly into the wrong shape — a block becomes a sibling of the key it belonged under, and nothing complains. Diff
  the rendered output; reading templates does not catch this class at all.
- **Non-determinism.** `randAlphaNum`, `uuidv4`, `now`, and anything derived from them make every render different.
  The consequences are a permanent drift in GitOps and, worse, a credential rotated on every upgrade while the
  consumers keep the old one. The `lookup`-guarded pattern is the accepted fix, and it has a sharp edge worth checking
  explicitly: **`lookup` returns empty under `helm template` and under any client-side render**, so the guard silently
  falls through to regeneration exactly where it was supposed to protect.
- **Checksum annotations.** Is the pod rolled when a mounted ConfigMap or Secret changes? A missing checksum means a
  config change with no restart, which is a silent no-op; a checksum computed over a template containing random data
  means a restart on every reconcile.
- **Subchart value plumbing.** A parent that sets a subchart value under the wrong key gets no error — unknown keys
  are simply ignored — so the setting quietly does nothing. Verify by rendering the subchart's object and reading the
  field, never by reading the parent's `values.yaml`.
- **`Release.IsInstall` / `IsUpgrade`** used for logic that must also hold on a re-install after a failed install, and
  hardcoded namespaces where `.Release.Namespace` belongs.

## `error-model` — where a bad value surfaces

Rank each class of bad input by where it lands: rejected by the schema at `helm install` (best), a render-time `fail`
or `required` (good), an API server rejection at apply (tolerable), a pod that starts and misbehaves (worst). The
finding is the distance between where it lands today and where it could land.

- `required "…"` and `fail` messages must name the value path and what to set. "value is required" names nothing.
- JSON Schema violation text is poor by default; a `title` and `description` on the property is what makes it
  readable, so schema coverage without descriptions is only half the fix.
- Mutually exclusive values that render into something half-working should `fail` instead. Enumerate the combinations
  the schema permits and the chart does not support — that gap list is the most useful artifact this surface produces
  for `error-model`.

## `security`

Secrets passed as plaintext values, and whether the chart offers the `existingSecret` escape hatch; anything secret
rendered into a ConfigMap, into `NOTES.txt`, or into an annotation. Image references pinned by tag or digest, the
pull-policy that pairs with each, and whether the registry is overridable for an air-gapped install. Pod security
context: `runAsNonRoot`, dropped capabilities, `readOnlyRootFilesystem`, seccomp, `automountServiceAccountToken`, and
any `hostPath`, `hostNetwork`, or `privileged`. RBAC breadth, wildcard verbs, and cluster scope where namespace scope
would do. Dependency provenance: where each dependency is fetched from, at which version, and whether it is verified.

## Tooling

```bash
helm version                                            # v3 and v4 differ; say which produced your evidence
helm dependency build <chart>                           # Chart.lock must resolve before anything else means much
helm lint --strict <chart>
helm template rel <chart> > work/render-default.yaml    # then read the output, not the templates
helm template rel <chart> -f <chart>/profiles/prod.yaml > work/render-prod.yaml
helm template rel <chart> --kube-version 1.25.0         # the low end of the declared kubeVersion range
kubeconform -strict -summary -schema-location default work/render-default.yaml
helm install rel <chart> --dry-run=server               # real validation, defaulting, admission — needs a cluster
helm unittest <chart>                                   # if the project has suites; note it if it does not
ct lint --charts <chart>
```

The command that answers the compatibility question, and the one most reviews skip:

```bash
git worktree add work/prev <previous-release-tag>
helm template rel work/prev/<chart> > work/render-prev.yaml
diff -u work/render-prev.yaml work/render-default.yaml   # every renamed object and changed immutable field is here
```

**`helm template` is not `helm install`, and the difference generates wrong findings in both directions.** Under
`helm template` there is no API server: `lookup` returns empty, `.Capabilities` is a static fake, CRDs in `crds/` are
not applied so custom resources are never validated against them, defaulting and admission do not run, and no
immutable-field conflict can appear. So —

- a defect **observed only in a local render** is `PLAUSIBLE` until it is reproduced with `--dry-run=server` or an
  actual install into a throwaway namespace;
- a defect **refuted only by a local render** is not refuted at all — say what the render cannot model and leave the
  finding standing;
- anything about validation, admission, capabilities, `lookup`, immutability, or upgrade behavior must go through a
  real cluster. A `kind` cluster costs a minute and settles most of this section.

And reading a template is not rendering it. A finding sourced from reading alone is `inferred`, however obvious the
bug looks.

## Architectural questions this surface raises

For the `architecture` distiller, not for the evidence axes:

- Is one umbrella chart with N conditional subcharts the right decomposition, or does enabling one component drag a
  user through the values of twenty? What would break if the components shipped as separate charts?
- Who owns the CRDs — this chart, a separate CRD chart, or the cluster administrator — and does that split survive
  an upgrade, an uninstall, and a GitOps prune performed by somebody who does not know the answer?
- Is the values surface a designed API, or a shadow of the current template layout? Could the templates be
  restructured without changing a single value name?
- Where the same block is copy-pasted across subcharts, what is the argument against a library chart — and what
  happens today when one copy is fixed and the others are not?
- Is Helm the right packaging for the ordering and convergence this system needs, or are hooks standing in for a
  controller that should exist?
