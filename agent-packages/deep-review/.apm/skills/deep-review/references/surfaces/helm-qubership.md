# Surface pack: Qubership / NC platform chart contract

An **organization overlay** on `surfaces/helm.md`. Read that pack first; this one adds the platform contracts a
Qubership product chart is expected to honor, so that a deployment engineer can set the same parameter name on every
microservice in a solution and have it mean the same thing.

Pass this surface only when the chart actually participates in the contract. It is opt-in for exactly that reason: the
rules below are the organization's, not Helm's, and applied to a chart outside their scope they generate a page of
confident findings about parameters that were never meant to exist.

## When this pack applies

The chart is a **product or project microservice chart** deployed through the platform's deployment tooling (CMDB and
cloud-deployer, or the ArgoCD repository template that replaced it). Positive markers, any of which is close to
conclusive:

- a `resource-profiles/` directory beside the chart with profiles named for environments;
- `values.schema.json` properties carrying the `internal` and `envSpecific` flags;
- values named `SERVICE_NAME`, `DEPLOYMENT_RESOURCE_NAME`, `REPLICAS`, `MEMORY_LIMIT`, `CLOUD_TOPOLOGY_KEY`.

It does **not** apply to an operator chart that installs upstream components, to vendored third-party subcharts, or to
a chart whose profiles select an internal preset rather than the platform's environment profiles. Two checks separate
these cheaply: `grep` the chart for `SERVICE_NAME` and `CLOUD_TOPOLOGY_KEY`, and read one profile file — a profile
holding a single `global.profile: <size>` line is a different mechanism with the same directory name, not a broken
implementation of this one. Where the answer is "does not apply", say so in the profile in one line and skip the pack.
Reporting the absence of the whole contract as a defect is the failure mode this section exists to prevent.

When the chart is in scope only partly — for example, it honors the resource-profile contract but predates the
topology one — review the parts it claims and name the rest as a gap for the maintainer to accept or decline, at
`LOW`, once.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Contracted parameter names, their placement between `values.yaml` and the profiles, `internal` / `envSpecific` flags, schema entries | `api-ux` |
| The three-year parameter window; renaming or dropping any parameter; a new required parameter; the `CLOUD_TOPOLOGY_KEY` deprecation path; a default appearing where the contract forbids one | `api-compatibility` |
| Rendering each profile and each strategy value; the strategy and topology blocks in the workload templates | `deployment-config` |
| Type coercion of `maxSurge` / `maxUnavailable` and of numeric profile values through the deployment tooling | `correctness` |

Every finding must cite the contract document and, where the document is versioned, the entry it relies on — several
of these rules have changed, and a finding written against a superseded revision is worse than none.

## Contract 0 — the three-year parameter window

**A chart must still install with the parameters that worked three years ago.** This is the organization's promise and
it outranks every other rule here: parameters are not removed, and no new parameter may be required. It is also the
one contract in this pack that is measured rather than argued — see *When the project states a compatibility window*
in `surfaces/helm.md` for the procedure, and run it before writing anything on this axis.

What follows from the promise:

- **A new parameter ships with a working default.** Not a documented default, a rendering one: any values file from
  the window omits the key, so the template path taken when it is absent is the only one that matters. A new
  `required` in `values.schema.json`, or a `required` call in a template, breaks the promise the day it merges.
- **Removal is replaced by a shim, and the shim is rendered, not assumed.** The old key stays readable and maps to the
  new one; precedence when both are set is documented and covered by a render test. An alias nobody exercised with
  both keys present is the failure mode — it usually drops the old value in silence.
- **Tightening `values.schema.json` is a removal in disguise.** A new `enum`, `pattern`, `minimum`, or
  `additionalProperties: false` rejects a values file that installed yesterday, without a single template changing.
- **Deprecated is not gone.** A parameter marked deprecated must keep working for the rest of the window; the finding
  is a deprecation with no read path, not a deprecation that lingers.
- **The window bounds severity.** A break inside three years is `HIGH` — an installation that the platform promised
  would work stops working, usually during someone's upgrade. Outside it, it is an ordinary compatibility question.
- **The promise covers installability, not semantics.** A changed default still installs and still changes behavior
  for every release that omits the value; report it, and say plainly that the policy does not cover it rather than
  arguing it does.

The promise also explains why CRD migration is a quieter question on these charts than the generic Helm pack implies:
upgrades are routine because inputs never break, and CRDs are typically owned outside the workload chart. Do not read
it as coverage, though — a parameter policy makes no statement about CRD schemas or persisted data, and the delete
cascade from a CRD rendered under `templates/` behaves exactly the same on a chart with a perfect parameter record.
Check that path on its own terms.

## Contract 1 — resource profiles

Profiles carry the environment-specific resource parameters. They live in `resource-profiles/` beside the chart, in
YAML, one file per profile, and **at least four profiles are mandatory**: `dev`, `prod`, `dev-ha`, `prod-nonha`.

- A parameter that appears in a profile **must not also appear in `values.yaml`**, and in `values.schema.json` it must
  carry both `"internal": true` and `"envSpecific": true`. A contracted parameter present in `values.yaml` is a real
  finding: the profile no longer overrides cleanly and the effective value depends on ordering. This is not a removal
  under Contract 0 — the parameter stays readable and a user setting it still wins — but it does delete a default,
  so the template path taken when no profile supplies the value has to render and has to be sane. Check that path.
- The contracted names are reserved and case-sensitive: `MEMORY_LIMIT`, `MEMORY_REQUEST`, `CPU_LIMIT`, `CPU_REQUEST`,
  `REPLICAS`, `MEM_ARGS`, `JDK_JAVA_OPTIONS`, the `HPA_*` family, the `PG_*` connection-pool family, and
  `NGINX_WORKER_PROCESSES`. A chart is free to add its own parameters; the contracted ones may not be spelled
  differently. `JAVA_OPTS` / `JAVA_OPTIONS` are deprecated in favor of `JDK_JAVA_OPTIONS` — report their use as
  deprecation, not as a defect.
- A profile that changes memory for a Java service and leaves `MEM_ARGS` untouched is a defect: the heap will not
  follow the container.
- Memory limit equal to memory request **is a recommendation, not a rule** — it was mandatory until 22 May 2025 and is
  now the strongly recommended default for out-of-the-box profiles, with delivery teams free to diverge and owning the
  consequences. Report a divergence in a shipped OOB profile at `LOW`; do not report it as a contract violation, and
  do not report it at all for a profile a project supplied.
- Profiles must differ in the ways their names promise. Identical `prod` and `prod-nonha`, or an `-ha` profile with
  `REPLICAS: 1`, is the finding the profile mechanism exists to prevent.
- The contract does not cover configuration items in the deployment descriptor; do not extend it to them.

Render every profile — that is the whole test — and check `HPA_MIN_REPLICAS <= HPA_MAX_REPLICAS`, that `REPLICAS` is
consistent with the HPA bounds when `HPA_ENABLED` is true, and that units are what the API expects.

## Contract 2 — deployment strategy

`DEPLOYMENT_STRATEGY_TYPE` selects one of four named strategies, with a fifth (default) branch, and
`DEPLOYMENT_STRATEGY_MAXSURGE` / `DEPLOYMENT_STRATEGY_MAXUNAVAILABLE` parameterize the custom one. The contract
mandates the template block **verbatim, including letter case**, which makes this the most mechanically checkable rule
in the pack: diff the chart's block against the canonical one and quote the diff as evidence.

For `Deployment`:

```yaml
spec:
  strategy:
    {{- if eq (default "" .Values.DEPLOYMENT_STRATEGY_TYPE) "recreate" }}
    type: Recreate
    {{- else if eq (default "" .Values.DEPLOYMENT_STRATEGY_TYPE) "best_effort_controlled_rollout" }}
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 0
      maxUnavailable: 80%
    {{- else if eq (default "" .Values.DEPLOYMENT_STRATEGY_TYPE) "ramped_slow_rollout" }}
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    {{- else if eq (default "" .Values.DEPLOYMENT_STRATEGY_TYPE) "custom_rollout" }}
    type: RollingUpdate
    rollingUpdate:
      maxSurge: {{ .Values.DEPLOYMENT_STRATEGY_MAXSURGE | default "25%" }}
      maxUnavailable: {{ .Values.DEPLOYMENT_STRATEGY_MAXUNAVAILABLE | default "25%" }}
    {{- else }}
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    {{- end }}
```

For `DeploymentConfig` the same selector drives OpenShift's spelling: `type: Rolling` with `rollingParams` in place of
`type: RollingUpdate` with `rollingUpdate`, and `type: Recreate` unchanged.

Checks:

- All three parameters are declared in `values.schema.json`, `DEPLOYMENT_STRATEGY_TYPE` as a string with the four-value
  `enum`, both others as **strings** — they accept `50%` as readily as `2`, so a schema that types them as integers is
  a defect, and so is a template that renders them unquoted into an `IntOrString` field. The deployment tooling has a
  known type-cast weakness here; a value that survives `helm template` can still arrive wrong through the pipeline.
  Treat a numeric spelling as a finding even when the local render looks fine, and say which of the two you tested.
- The strategy is a **solution-wide** setting: every microservice in the application carries the same block. A chart
  that implements it for one workload and not another is the defect the contract's "all microservices" clause names.
- Per-service strategy overrides are explicitly out of contract. Do not propose one.

## Contract 3 — topology spread constraints

Every `Deployment` renders `topologySpreadConstraints` from `CLOUD_TOPOLOGIES` when it is set, and from
`CLOUD_TOPOLOGY_KEY` otherwise. `CLOUD_TOPOLOGIES` is an array whose items carry a mandatory `topologyKey` and
optional `maxSkew` (default `1`) and `whenUnsatisfiable` (default `ScheduleAnyway`); the label selector matches
`coalesce DEPLOYMENT_RESOURCE_NAME SERVICE_NAME`.

- `CLOUD_TOPOLOGIES` takes priority over `CLOUD_TOPOLOGY_KEY` and **must not carry a default in `values.yaml`** — a
  default there silently overrides nothing and disables the fallback. `CLOUD_TOPOLOGY_KEY: kubernetes.io/hostname`
  belongs in `values.yaml`.
- The block renders **for every resource profile**, not only the default one. Render each profile and confirm.
- Both parameters need schema entries: `CLOUD_TOPOLOGIES` as an array, `CLOUD_TOPOLOGY_KEY` as a string with the
  documented default.
- `CLOUD_TOPOLOGY_KEY` is on a deprecation path — deprecated in 24.2, with removal planned for 24.4, at which point
  `CLOUD_TOPOLOGIES` gains the default `- topologyKey: kubernetes.io/hostname`. **That plan contradicts Contract 0**,
  which forbids removing a parameter inside the three-year window, and Contract 0 wins: the key keeps its read path
  and its documented behavior until the window closes, whatever the topology guide scheduled. A chart that dropped it
  on the 24.4 boundary is a finding, and so is a chart that stopped rendering the fallback while still accepting the
  value. Establish which release line the chart targets, cite it, and cite both documents — this is a contract
  conflict for the maintainer to resolve, not a defect you get to settle by picking the guide you prefer.

## Out of scope for this pack

The source guides carry material that is context rather than a checkable rule, and a finding built on it will not
survive triage: deployment-tooling UI plans and their implementation status, measured rollout durations for a
particular replica count and probe timing, guide changelogs, ownership and approval metadata, and open questions the
authors left for themselves. Use them to understand intent; do not cite them as an expectation.

Likewise, this pack says nothing about Helm craft — falsy defaults, list merge semantics, immutable selectors, CRD
lifecycle. That is `surfaces/helm.md`, and it applies to these charts in full.
