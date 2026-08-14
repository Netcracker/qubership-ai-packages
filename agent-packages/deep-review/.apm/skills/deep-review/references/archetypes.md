# Archetypes and axis selection

Two independent choices, and confusing them produces a review that misses the obvious. The **archetype** decides
*which axes run*. The **surfaces** decide *what each axis knows about the form of the API* — see
`references/surfaces/`. A Kubernetes operator and a REST service may run the same axis list; what differs is that one
axis reads `surfaces/kubernetes.md` and the other reads `surfaces/rest-http.md`, and those disagree about naming,
about what a breaking change is, and about where the expectation in a finding may be sourced from.

One repository usually has more than one surface. Pick them at profiling time and pass all of them.

Classify the repository first. The archetype decides which axes are worth an agent and which would produce a section
nobody asked for. When a repository is two things at once (a library plus its CLI), take the union and say so in the
profile.

## Archetypes

- **library** — consumed as a dependency, no process of its own. The public API is the product.
- **protocol library** — a library whose product is conformance to an external specification (a wire protocol, a file
  format, a standard). Interop with other implementations is the acceptance criterion.
- **service** — a long-running process with its own deployment, configuration, and on-call.
- **operator / controller** — a service whose API is Kubernetes resources and whose job is convergence.
- **cli** — invoked by humans and scripts; the argument surface and exit codes are the product.
- **mcp-server / agent-tool** — invoked by models; tool names, schemas, and error text are the product.
- **sdk / client** — a library whose product is fidelity to a remote API it does not own.
- **monorepo** — several of the above. Profile each component, pick axes per component, and say in the focus file which
  component each axis targets.

## Axis matrix

`y` = run by default, `?` = run if the focus file says so, blank = skip.

| Axis | library | protocol lib | service | operator | cli | mcp | sdk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tests` | y | y | y | y | y | y | y |
| `correctness` | y | y | y | y | y | y | y |
| `error-model` | y | y | y | y | y | y | y |
| `concurrency-lifecycle` | y | y | y | y | ? | ? | y |
| `api-compatibility` | y | y | ? | y | y | y | y |
| `api-ux` | y | y | ? | y | y | y | y |
| `protocol-conformance` | | y | ? | | | y | y |
| `performance` | ? | y | ? | ? | | | ? |
| `dependencies` | y | y | y | y | y | y | y |
| `security` | ? | y | y | y | ? | y | y |
| `docs-onboarding` | y | y | y | y | y | y | y |
| `build-release` | y | y | ? | ? | y | y | y |
| `observability-operability` | ? | ? | y | y | ? | ? | ? |
| `deployment-config` | | | y | y | | | |
| `data-lifecycle` | ? | | y | y | | | ? |
| `architecture` | y | y | y | y | y | y | y |

`architecture` is always a **synthesis** axis: it runs last, on a prompt distilled from the evidence axes. `api-ux` is
a synthesis axis when the repository already has review history to distil from, and an evidence axis otherwise.

## Sizing

A default run is 5–8 evidence axes plus `architecture`. More than ten axes on one repository usually means the profile
is too coarse: split the monorepo, or narrow the focus to the part that is changing.

Cheap first: `tests` and `dependencies` are fast and they tell the other axes where to dig. Put them in the first
phase even when they are not the interesting part.

## Worked examples

**A Diameter transport library (Java).** Archetype: protocol library. Axes: `tests`, `protocol-conformance`,
`concurrency-lifecycle`, `error-model`, `correctness`, `api-compatibility`, `api-ux`, `performance`, `docs-onboarding`,
then `architecture`. Skip `deployment-config`, `data-lifecycle`, `observability-operability` (keep only the "does it
let the host observe it" half, folded into `api-ux`).

**A Kubernetes operator.** Archetype: operator. Surfaces: `kubernetes`, plus `helm` when it ships an install chart,
plus `rest-http` if it also serves one. `kubernetes` covers the CRD it serves and `helm` the values contract of the
chart that installs it; they are two APIs with two audiences, and one pack will not do for both. Axes:
`tests`, `correctness`, `concurrency-lifecycle`, `api-ux`, `error-model`, `observability-operability`,
`deployment-config`, `api-compatibility`, `security`, then `architecture`. The CRD schema, the condition vocabulary,
and CRD versioning look like three different axes' work and are three different axes' work — `surfaces/kubernetes.md`
routes them. `protocol-conformance` becomes the contract with whatever backend it drives; run it with the backend's
source as an input.

**An MCP server that wraps an existing CLI.** Archetype: mcp-server, plus `cli` if the repository owns the binary as
well. Surfaces: `mcp`, and `cli` when the same repository ships both — they are two audiences for one core, and the
drift between them is a finding neither pack produces alone. Axes: `tests`, `api-ux`, `error-model`,
`protocol-conformance`, `correctness`, `security`, `api-compatibility`, `docs-onboarding`, then `architecture`. Pin the
protocol revision in the profile before any axis starts; `surfaces/mcp.md` says why.

## Surfaces available

`kubernetes`, `cli`, `mcp`, `helm`, `helm-qubership`, and `gitops-argocd` — `helm-qubership` is an organization overlay
on `helm`, opt-in and only for charts that participate in the Qubership platform parameter contract. Everything else —
`rest-http`, `grpc`, `graphql`, `events-messaging`, `code-library`, outgoing webhooks, a database schema shared between
services, a Terraform provider, emitted telemetry under OpenTelemetry semantic conventions — has no pack yet. Name the
surface in the profile anyway and note the gap: the axes will fall back to their form-independent rules, which is
weaker but honest. Write the pack from what that review
turns out to need, not from a guess.
