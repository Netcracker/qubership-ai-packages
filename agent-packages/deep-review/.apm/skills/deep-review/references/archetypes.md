# Archetypes and axis selection

Two independent choices, and confusing them produces a review that misses the obvious. The **archetype** decides
*which axes run*. The **surfaces** decide *what each axis knows about the form of the API* — see
`references/surfaces/`. A Kubernetes operator and a REST service may run the same axis list; what differs is that one
axis reads `surfaces/kubernetes.md` and the other, for a form that has no pack, falls back to its form-independent
rules, and those disagree about naming, about what a breaking change is, and about where the expectation in a finding
may be sourced from.

One repository usually has more than one surface. Pick them at profiling time and pass all of them.

Classify the target first. The archetype decides which axes are worth an agent and which would produce a section
nobody asked for. When a repository is two things at once (a library plus its CLI), take the union and say so in the
profile.

## Archetypes

- **library** — consumed as a dependency, no process of its own. The public API is the product.
- **protocol library** — a library whose product is conformance to an external specification (a wire protocol, a file
  format, a standard). Interop with other implementations is the acceptance criterion.
- **service** — a long-running process with its own deployment, configuration, and on-call. A microservice is a
  service; the interactions with its neighbors are reviewed as its surfaces (`rest-http`, or `events-messaging`, which
  has no pack yet) unless the neighbors are in the review too, which makes it a system.
- **operator / controller** — a service whose API is Kubernetes resources and whose job is convergence.
- **cli** — invoked by humans and scripts; the argument surface and exit codes are the product.
- **mcp-server / agent-tool** — invoked by models; tool names, schemas, and error text are the product.
- **sdk / client** — a library whose product is fidelity to a remote API it does not own.
- **web-app** — a browser application (SPA or server-rendered) used by people; the journeys through its screens are
  the product. A UI component library published for reuse is a `library` that also runs `frontend-web`.
- **system** — several components reviewed together: several repositories, or several deployables of one monorepo.
  The product is the interactions: contracts between components, shared schemas and topics, failure propagation,
  deployment as a whole (an umbrella chart, an Argo CD application set). Each component gets a row in the profile with
  its own archetype; the axis list is one for the whole system, and the focus file says which components each axis
  reads closely.
- **monorepo** — one repository holding several components. Profile each component, and in the questions file propose
  the slices and an axis-by-slice matrix (`slice`, `paths`, `focus`, and `seams` in step 3 of `SKILL.md`). Run
  `contracts` on every monorepo, and on any repository that ships two components talking to each other, with the
  profile's seam list as its `seams`. When the interactions between the components are the question, profile it as a
  `system` as well; when the review is about one component, say so in the focus file and profile it under that
  component's archetype.

## Axis matrix

`y` = in the default set, `?` = applicable, run when the focus file says so, blank = does not apply. A review of that
archetype runs the default set when the questions file gives no reason to change it. On a service or an operator the
default set is larger than the limit in *Sizing* below, so the questions file proposes which of those axes to cut.
Every `?` is a legitimate axis for the archetype, and a directed question in the focus file is the usual reason to turn
one on.

| Axis | library | protocol lib | service | operator | cli | mcp | sdk | web-app | system |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tests` (scout) | y | y | y | y | y | y | y | y | ? |
| `dependencies` (scout) | y | y | y | y | y | y | y | y | ? |
| `test-strategy` | ? | ? | y | y | ? | ? | ? | ? | ? |
| `correctness` | y | y | y | y | y | y | y | y | ? |
| `error-model` | y | y | y | y | y | y | y | ? | y |
| `concurrency-lifecycle` | y | y | y | y | ? | ? | y | | ? |
| `api-compatibility` | y | y | ? | y | y | y | y | | y |
| `contracts` | | | ? | ? | | ? | ? | ? | y |
| `api-ux` | y | y | ? | ? | y | y | y | | ? |
| `protocol-conformance` | | y | ? | ? | | y | y | | ? |
| `performance` | ? | y | ? | ? | | | ? | ? | ? |
| `security` | ? | y | y | y | y | y | y | y | y |
| `docs-onboarding` | y | ? | ? | ? | y | y | y | ? | ? |
| `docs-pages` | ? | ? | y | y | ? | ? | ? | ? | ? |
| `build-release` | y | ? | ? | ? | y | y | ? | y | ? |
| `observability-operability` | ? | ? | y | y | ? | ? | ? | | y |
| `telemetry` | ? | ? | y | y | ? | ? | ? | ? | ? |
| `deployment-config` | | | y | y | | | | ? | y |
| `data-lifecycle` | ? | | y | ? | | | ? | | y |
| `upgrade-migration` | ? | ? | y | y | ? | ? | ? | ? | y |
| `frontend-web` | ? | | | | | | | y | ? |
| `least-surprise` | | | y | ? | y | ? | | y | ? |
| `runtime-verification` | | ? | ? | ? | ? | ? | ? | ? | ? |
| `architecture` | y | y | y | y | y | y | y | y | y |

`architecture` is always a **synthesis** axis: it runs last, on a prompt distilled from the evidence axes. `api-ux` is
a synthesis axis when the repository already has review history to distill from (earlier dossiers, a usability study,
a migration post-mortem), and an evidence axis otherwise. `runtime-verification` is a synthesis axis too: it runs
after the evidence axes have been verified and settles their findings against a running system, so it needs a runtime
the focus file allows and pays off most on an operator or a service.

The new axes run under these conditions:

- `test-strategy` runs by default for a service, an operator, and a monorepo of any archetype; elsewhere, run it when
  the repository has a medium or large test level, or a real peer (database, queue, another service) behind a double.
  It is an evidence axis that reads the `tests` scout report.
- `contracts` runs where two components of one repository meet (see the monorepo bullet above).
- `docs-pages` runs only where the repository ships user documentation beyond the README and a getting-started page:
  a `docs/` tree, a docs site, administration or configuration guides, a troubleshooting page. Without them,
  `docs-onboarding` covers the README alone.
- `telemetry` and `observability-operability` divide one subject: the first judges each call site, the second the
  outcome for the operator. Run `telemetry` for a library only when the focus file asks what the library emits into
  its host. When both run, `observability-operability` moves to the synthesis phase and reads the telemetry inventory.
- `frontend-web` needs a running application; the `library` cell means a UI component library. The profiler records
  the start commands and how the backend is provided in `00-commands.md`.
- `least-surprise` needs a surface a person operates: run it for a service only when it has a UI, a CLI, or chart
  values a person edits; for an operator when its CRD or chart is edited by hand; for an MCP server when a tool is
  destructive. Without a runtime it falls back to tracing and says so in its coverage.

## Sizing

A default run is five to eight evidence axes and `architecture`, plus the two scout axes on a single repository (a
system review turns them on per component when the focus file asks). More than ten axes on one target
usually means the review is asking too many questions at once: cut the axes the focus file cannot name a question
for, or lower the depth to `coarse`. Do not narrow the target to a subtree instead; a review of part of a repository
answers a question the profile did not ask, and the skill is not the tool for a class or a package.

Cheap first: `tests` and `dependencies` are fast and they tell the other axes where to dig. Put them in the first
phase even when they are not the interesting part.

## Worked examples

Each example is the default column of the matrix, with the `?` axes the focus file turned on and why.

**A Diameter transport library (Java).** Archetype: protocol library. Default: `tests`, `dependencies`,
`protocol-conformance`, `correctness`, `error-model`, `concurrency-lifecycle`, `api-compatibility`, `api-ux`,
`performance`, `security`, then `architecture`. Turned on: `docs-onboarding`, because the focus file asked whether a
new integrator can reach a first message without reading the source. `observability-operability` stays off: its
library mode (does it let the host observe it) is a directed question for `api-ux`, which reviews the host-facing
surface anyway. Skip `deployment-config` and `data-lifecycle`.

**A Kubernetes operator.** Archetype: operator. Surfaces: `kubernetes`, plus `helm` when it ships an install chart;
add `rest-http` when it also serves one. `kubernetes` covers the CRD it serves and `helm`
the values contract of the chart that installs it; they are two APIs with two audiences, and one pack will not do for
both. Default: `tests`, `dependencies`, `correctness`, `error-model`, `concurrency-lifecycle`, `api-compatibility`,
`security`, `observability-operability`, `deployment-config`, `upgrade-migration`, then `architecture`. Turned on:
`api-ux`, because the CRD schema is hand-authored and the focus file asked about it; `protocol-conformance` when the
operator drives a backend with its own protocol, with the backend's source as an input. The CRD schema, the condition
vocabulary, and CRD versioning look like three different axes' work and are three different axes' work —
`surfaces/kubernetes.md` routes them.

**An MCP server that wraps an existing CLI.** Archetype: mcp-server, plus `cli` if the repository owns the binary as
well. Surfaces: `mcp`, and `cli` when the same repository ships both — they are two audiences for one core, and the
drift between them is a finding neither pack produces alone. Default: `tests`, `dependencies`, `correctness`,
`error-model`, `api-compatibility`, `api-ux`, `protocol-conformance`, `security`, `docs-onboarding`, `build-release`,
then `architecture`. Pin the protocol revision in the profile before any axis starts; `surfaces/mcp.md` says why.

**Three microservices and the umbrella chart that deploys them.** Archetype: system, with three `service` rows and
one chart row in the components table. Surfaces: `helm`, `gitops-argocd`, `rest-http`; `events-messaging` in
`surfacesWithoutPack`. Default: `error-model`, `api-compatibility`, `contracts`, `security`, `observability-operability`,
`deployment-config`, `data-lifecycle`, `upgrade-migration`, then `architecture`. Turned on: `runtime-verification`,
because the focus file granted a disposable cluster and the question is whether a rolling upgrade of one service
breaks the other two. The focus file names the interactions each axis reads closely: `api-compatibility` reads the
two REST contracts and the topic schema, `data-lifecycle` the two services that share a database.

**An HTTP service with a published OpenAPI spec.** Archetype: service. Surfaces: `rest-http`, plus `helm` when it
ships a chart. Pin the contract artifact in the profile first: which spec file is published, whether it is
hand-written or generated from code, the previous release tag, and the gateway in front of the server
(`surfaces/rest-http.md`, "The contract artifact, first"). Axes: `tests`, `test-strategy`, `correctness`, `error-model`,
`security`, `contracts`, `api-compatibility`, `api-ux`, `protocol-conformance`, `telemetry`, and
`observability-operability` in the synthesis phase, then `architecture`.
Once the spec has consumers outside the repository, `api-compatibility`, `api-ux`, and `protocol-conformance` are
default rather than optional; with only the repository's own frontend as a caller, `contracts` covers most of what
`api-compatibility` would find.

## Surfaces available

`kubernetes`, `cli`, `mcp`, `rest-http`, `helm`, `helm-qubership`, and `gitops-argocd` — `helm-qubership` is an
organization overlay on `helm`, opt-in and only for charts that participate in the Qubership platform parameter
contract. Everything else — `grpc`, `graphql`, `events-messaging`, `code-library`, outgoing webhooks, a database schema
shared between services, a Terraform provider, emitted telemetry under OpenTelemetry semantic conventions — has no pack
yet. Name the surface in the profile anyway and pass it in `surfacesWithoutPack`: the axes fall back to their
form-independent rules, which is weaker but honest, and the gap shows up in coverage. Write the pack from what that
review turns out to need, not from a guess.
