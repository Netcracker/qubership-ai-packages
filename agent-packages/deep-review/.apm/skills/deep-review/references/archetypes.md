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
  service; the interactions with its neighbors are reviewed as surfaces without a pack (`rest-http`,
  `events-messaging`) unless the neighbors are in the review too, which makes it a system.
- **operator / controller** — a service whose API is Kubernetes resources and whose job is convergence.
- **cli** — invoked by humans and scripts; the argument surface and exit codes are the product.
- **mcp-server / agent-tool** — invoked by models; tool names, schemas, and error text are the product.
- **sdk / client** — a library whose product is fidelity to a remote API it does not own.
- **system** — several components reviewed together: several repositories, or several deployables of one monorepo.
  The product is the interactions: contracts between components, shared schemas and topics, failure propagation,
  deployment as a whole (an umbrella chart, an Argo CD application set). Each component gets a row in the profile with
  its own archetype; the axis list is one for the whole system, and the focus file says which components each axis
  reads closely.
- **monorepo** — one repository holding several components. Profile it as a `system` when the components interact and
  the interactions are the question; otherwise pick the one component the review is about, say so in the focus file,
  and profile it under its own archetype.

## Axis matrix

`y` = in the default set, `?` = applicable, run when the focus file says so, blank = does not apply. A review of that
archetype runs the default set when the questions file gives no reason to change it; the set is sized so that the run
stays under the limit in *Sizing* below. Every `?` is a legitimate axis for the archetype, and a directed question
in the focus file is the usual reason to turn one on.

| Axis | library | protocol lib | service | operator | cli | mcp | sdk | system |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tests` (scout) | y | y | y | y | y | y | y | ? |
| `dependencies` (scout) | y | y | y | y | y | y | y | ? |
| `correctness` | y | y | y | y | y | y | y | ? |
| `error-model` | y | y | y | y | y | y | y | y |
| `concurrency-lifecycle` | y | y | y | y | ? | ? | y | ? |
| `api-compatibility` | y | y | ? | y | y | y | y | y |
| `api-ux` | y | y | ? | ? | y | y | y | ? |
| `protocol-conformance` | | y | ? | ? | | y | y | ? |
| `performance` | ? | y | ? | ? | | | ? | ? |
| `security` | ? | y | y | y | y | y | y | y |
| `docs-onboarding` | y | ? | ? | ? | y | y | y | ? |
| `build-release` | y | ? | ? | ? | y | y | ? | ? |
| `observability-operability` | ? | ? | y | y | ? | ? | ? | y |
| `deployment-config` | | | y | y | | | | y |
| `data-lifecycle` | ? | | y | ? | | | ? | y |
| `upgrade-migration` | ? | ? | y | y | ? | ? | ? | y |
| `runtime-verification` | | ? | ? | ? | ? | ? | ? | ? |
| `architecture` | y | y | y | y | y | y | y | y |

`architecture` is always a **synthesis** axis: it runs last, on a prompt distilled from the evidence axes. `api-ux` is
a synthesis axis when the repository already has review history to distill from (earlier dossiers, a usability study,
a migration post-mortem), and an evidence axis otherwise. `runtime-verification` is a synthesis axis too: it runs
after the evidence axes have been verified and settles their findings against a running system, so it needs a runtime
the focus file allows and pays off most on an operator or a service.

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
`rest-http` goes into `surfacesWithoutPack` when it also serves one. `kubernetes` covers the CRD it serves and `helm`
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
one chart row in the components table. Surfaces: `helm`, `gitops-argocd`; `rest-http` and `events-messaging` in
`surfacesWithoutPack`. Default: `error-model`, `api-compatibility`, `security`, `observability-operability`,
`deployment-config`, `data-lifecycle`, `upgrade-migration`, then `architecture`. Turned on: `runtime-verification`,
because the focus file granted a disposable cluster and the question is whether a rolling upgrade of one service
breaks the other two. The focus file names the interactions each axis reads closely: `api-compatibility` reads the
two REST contracts and the topic schema, `data-lifecycle` the two services that share a database.

## Surfaces available

`kubernetes`, `cli`, `mcp`, `helm`, `helm-qubership`, and `gitops-argocd` — `helm-qubership` is an organization overlay
on `helm`, opt-in and only for charts that participate in the Qubership platform parameter contract. Everything else —
`rest-http`, `grpc`, `graphql`, `events-messaging`, `code-library`, outgoing webhooks, a database schema shared between
services, a Terraform provider, emitted telemetry under OpenTelemetry semantic conventions — has no pack yet. Name the
surface in the profile anyway and pass it in `surfacesWithoutPack`: the axes fall back to their form-independent
rules, which is weaker but honest, and the gap shows up in coverage. Write the pack from what that review turns out to
need, not from a guess.
