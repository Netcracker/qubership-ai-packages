# Surface pack: GitOps / Argo CD

Apply this pack when the repository's artifacts are deployed by a GitOps controller rather than by a human running
`helm install` — an Argo CD `Application`, Flux `HelmRelease` or `Kustomization`, or an organization that states
GitOps as the delivery path. It is opt-in: applied to a chart nobody syncs, it produces a page of findings about a
controller that will never touch it.

The distinguishing fact is not the tool. It is that **something re-applies the desired state on a loop, forever,
and compares it against the cluster**. That turns three things into contract that a human-driven install never
exercises: field ownership, drift detection, and health assessment. A chart can install perfectly by hand and still
be permanently `OutOfSync` under Argo.

A surface pack is a lens, not an axis. Several axes read this file, so **it says who owns what** — stay inside your
row and leave the rest alone.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Fields the controller writes into objects the user declares; `spec` mutated in place; generated values that differ per render | `correctness` |
| Health assessment of custom resources; what a reader sees in the Argo UI when the thing is broken; `Progressing` versus `Degraded` versus `Healthy` | `error-model` |
| Sync waves and hook phases; prune order; CRD ownership across two Applications; `ServerSideApply` and field-manager conflicts | `deployment-config` |
| Renaming or moving a rendered object; changing an immutable field; anything that makes a sync fail on an existing installation | `api-compatibility` |
| Non-determinism across renders; `lookup`, timestamps, random values | `correctness` |
| Whether removing a resource from git actually removes it from the cluster, and what it takes with it | `data-lifecycle` |

## Normative sources

Cite a section, not a memory.

- **Argo CD docs**: *Sync Options*, *Sync Phases and Waves*, *Resource Hooks*, *Diffing Customization*,
  *Resource Health*, *Server-Side Apply*.
- **Kubernetes Server-Side Apply** documentation for field managers and conflict semantics — the mechanism under
  `ServerSideApply=true`.
- **Helm hook to Argo phase mapping**: Helm `pre-install`/`post-install`/`pre-delete`/`post-delete` are translated,
  and the translation is lossy. Which Helm hooks the project relies on, and what they become, is checkable.

Where the project documents its own Argo procedure, that wins — cite the local text and report the divergence
rather than the upstream rule.

## The checks that pay

### Idempotent render

Render twice and diff. Anything that differs between two renders of the same inputs makes the Application
permanently `OutOfSync`, and the operator learns to ignore the status:

```bash
helm template <release> <chart> -f <values> >a.yaml
helm template <release> <chart> -f <values> >b.yaml
diff a.yaml b.yaml
```

Usual culprits: `randAlphaNum` for a secret with no `lookup` guard, `now`, a checksum over something that itself
varies, `Release.Revision` in a name or label.

The secret case deserves its own note, because it fails in two opposite ways. A password generated at render time
without a `lookup` guard is regenerated on every sync — the Application never converges and the credential rotates
under running workloads. Guarded with `lookup`, it becomes empty during `helm template` and diff previews. Say
which of the two the chart does.

### Field ownership

The controller must not write into `spec` of an object the user declares in git. GitOps re-applies `spec`; the
controller writes it back; the two fight forever and the resource flaps between `Synced` and `OutOfSync`.
Enumerate every field the controller writes and check which of them are user-declared.

Under `ServerSideApply=true` the same conflict surfaces as a field-manager error rather than a flap. Both are
defects; they read differently in the UI, so name which one the reader will see.

### Prune and ownership of shared objects

- **CRDs.** A chart's `crds/` directory has a protected lifecycle; a separate CRD Application does not. Which
  Application owns them, what happens when both are pointed at the same CRDs, and what a prune does to custom
  resources still using them.
- **Cluster-scoped objects** with hardcoded names: two Applications of the same chart in two namespaces collide,
  and whichever syncs last owns the object.
- **Deletion order.** Argo prunes on its own schedule. If the project's cleanup depends on a controller and its
  RBAC still existing while finalizers drain, a prune that removes RBAC first wedges the namespace. Test the
  documented order and one wrong order.

### Health

Argo reports a custom resource as `Healthy` unless it knows better. For CRs this project creates, does the status
carry enough for Argo's built-in or a custom health check to tell working from broken? A resource that is
`Healthy` in the UI while its workload cannot schedule trains the operator to distrust the dashboard — report it
here, and let `error-model` own the condition vocabulary that causes it.

### Hooks under Argo

Helm hooks become Argo phases, and the mapping is version-dependent — `PreDelete` support in particular arrived
late. A hook the project relies on for correctness (cleanup, migration, credential creation) that silently does
not run under the organization's Argo version is a defect, and the Argo version is a fact to establish, not assume.

## What counts as a breaking change here

Wider than for a hand-installed chart. All of these break existing Applications even though the values contract
is untouched:

- renaming a rendered object, or moving it between namespaces or scopes;
- changing an immutable field (`Service.spec.clusterIP`, `Deployment.spec.selector`, `volumeClaimTemplates`);
- adding a resource that collides by name with one another Application already owns;
- changing which Application owns the CRDs;
- introducing a render-time non-determinism where there was none.

## Rejection rules

- **Argo is not installed in the review cluster** — say so and mark the finding `traced`, do not silently
  downgrade the whole section. Render-determinism, field-ownership and name-collision checks do not need Argo and
  must still be executed.
- A concern about `helm install` that GitOps does not change belongs to `deployment-config`.
- "Argo could be configured to ignore this" is not a refutation unless the project ships that configuration.
- Preferences about repository layout, Application-of-Applications style, or directory structure are out of scope
  unless the project states a convention.
