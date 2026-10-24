# Surface pack: HTTP API

Apply this pack when the repository serves an HTTP API that somebody else calls: a REST or REST-ish service, usually
described by an OpenAPI document, consumed by a browser app, a generated SDK, another service, a script, or an agent.
It also applies to the HTTP half of a repository whose main product is something else: an operator with an admin API,
a CLI with a `serve` subcommand. It does not apply to a client of someone else's HTTP API (that is the `sdk / client`
archetype, judged against the remote spec), nor to health and metrics endpoints that only a probe and a scraper call;
those belong to `observability-operability` and `telemetry`.

The contract here is the published API description and the behavior behind it, not the router code. The callers have
not read the handlers. A generated client reads the spec and nothing else, a browser app was written against last
month's spec, a script reads the status code, and an agent reads `summary`, `description`, and the error body. Each
fails differently when the spec and the server disagree, and most real defects on this surface live in that gap.

A surface pack is a lens, not an axis. Several axes read this file, so **it says who owns what**: stay inside your row
of the table below and leave the rest alone. A concern raised twice in two vocabularies costs the reader more than it
costs you. The pack has no finding prefix of its own; every finding carries the prefix of the axis that owns it.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Path and resource naming; one concept, one name across operations; parameter and field naming and casing; pagination, filtering, sorting, and field-selection design; defaults and units; response volume and empty collections; `operationId`, `summary`, `description`, and `example` as the only documentation a generated client or an agent gets; lint findings from the style ruleset that cost a caller | `api-ux` |
| Which condition maps to which status code, and whether the mapping is the same in every operation; a failure reported with a `2xx`; the error body shape and its stable machine identity (problem `type`, a `code` field); message content; retryable versus final (`Retry-After`, `503` versus `500` versus `409`); partial success in batch endpoints; what the caller receives when a timeout, a rate limit, or a size limit fires | `error-model` |
| RFC 9110 obligations: safe methods without side effects, idempotent `PUT` and `DELETE`, the headers a status code requires (`Allow` on `405`, `WWW-Authenticate` on `401`, no body on `204` and `304`), `HEAD` and `OPTIONS`, conditional requests and ETag comparison, content negotiation (`406`, `415`, `Vary`); RFC 9111 cache directives; RFC 9457 member types and media type; RFC 8288 `Link` syntax and relation names | `protocol-conformance` |
| What changed in the published contract between the previous release and `HEAD`, as an external consumer sees it: every item under *What counts as a breaking change*; the diff gate in CI; the versioning strategy and whether practice matches it; deprecation signaling and support windows | `api-compatibility` |
| Agreement at one commit between the spec, the server, and every client the repository ships (generated SDK, the frontend's API layer, service-to-service clients, e2e collections); spec validity as a machine artifact; a committed generated spec that no longer matches a regeneration; operations, parameters, fields, and status codes declared but not implemented, or implemented but not declared; skew between the repository's own components during a rolling deployment | `contracts` |
| Handler logic behind a conforming contract: duplicate creation when a client retries a `POST`, an `Idempotency-Key` accepted and then not honored, cursors that skip or repeat rows under concurrent writes, null versus absent versus empty, `PATCH` semantics against the declared patch format | `correctness` |
| Lost updates on read-modify-write with no precondition; in-flight requests on graceful shutdown; streaming responses and work that continues after the client disconnects | `concurrency-lifecycle` |
| Authentication declared versus enforced; object- and function-level authorization; mass assignment of read-only fields; CORS; unbounded input size (body, page size, array length, decompression, multipart); rate limiting where the threat model needs it; secrets and personal data in responses, error bodies, and logs; SSRF in URL-valued parameters; authenticated responses stored by shared caches | `security` |
| The cost of a legitimate request: queries per list page, cost that grows with the dataset rather than the page, buffering a whole payload where streaming was possible, measured response sizes | `performance` |
| Request logs, metrics, and spans on HTTP handlers: route template versus raw path as a label, OpenTelemetry HTTP semantic conventions, `traceparent` in and out, how errors are classified in metrics, a request ID echoed to the caller | `telemetry` |
| Health and readiness endpoints and what they check; timeout ordering along the chain from load balancer to handler to downstream; the on-call drill for an API failure | `observability-operability` |
| From the README to the first successful authenticated call: base URL, how to obtain a credential, a first request that works, a reference reachable from the README | `docs-onboarding` |
| Hand-written pages about the API (guides, tutorials, reference prose) against the spec and the server: examples that run, status codes and errors the pages list | `docs-pages` |
| Names, summaries, and product text that promise behavior the endpoint does not perform: a `dryRun` that writes, an `archive` that deletes, a "returns all items" that pages. Where the behavior also breaks an RFC requirement, such as a `GET` that writes, `protocol-conformance` owns it | `least-surprise` |
| A test per documented status code and error type; a snapshot of the spec so a contract change shows in review; tests through the real HTTP stack rather than the handler function | `tests` |
| Whether a test runs the spec against the server; which level each contract check runs at (handler unit test, in-process HTTP, spec-driven property test, deployed e2e collection) and the gaps and duplicates across levels | `test-strategy` |
| The browser app as a caller: how it handles each error status and problem body, session expiry, pagination, and repeated submission of a non-idempotent call | `frontend-web` |
| What `DELETE` removes, soft delete, retention, and export endpoints | `data-lifecycle` |
| Framework and code-generator versions; the spec and generated clients as release artifacts; `info.version` discipline | `dependencies`, `build-release` |

Two boundaries cause most duplicates. **`contracts` versus `api-compatibility`**: the first compares artifacts at one
commit, or two of the repository's own components deployed side by side; the second compares the published contract
at two releases, for a consumer the repository does not control. **`error-model` versus `protocol-conformance`**: the
first owns the choice of status and body for a condition and its consistency; the second owns what RFC 9110 and RFC
9457 require once that choice is made.

## Normative sources

Fetch these rather than recalling them; the expectation in a finding must cite a section, not a memory.

- **RFC 9110, HTTP Semantics.** §9.2.1 safe methods, §9.2.2 idempotent methods, §9.3 method definitions, §8.8
  validators (`ETag`, `Last-Modified`), §10.2 response context fields (`Allow`, `Location`, `Retry-After`), §11
  authentication, §12 content negotiation, §13 conditional requests, §15 status codes. Each status code subsection
  states what a response with that code must carry; quote it.
- **RFC 9111, HTTP Caching**, where responses carry cache directives or pass through a CDN or shared proxy: §5.2
  `Cache-Control`, and what `private` and `no-store` mean for an authenticated response.
- **RFC 9457, Problem Details for HTTP APIs** (obsoletes RFC 7807): §3.1 standard members and their types, §3.2
  extension members, §4 defining a problem type, §6 the `application/problem+json` media type.
- **RFC 8288, Web Linking**, and the IANA link relations registry for `next`, `prev`, `first`, `last`.
- **RFC 9745** (`Deprecation` header) and **RFC 8594** (`Sunset` header) for in-band deprecation.
- **The OpenAPI Specification** at the version the document declares in `openapi:`. 3.0.x uses its own subset of JSON
  Schema (`nullable`, no `type` arrays, no `const`); 3.1 aligns with JSON Schema 2020-12 and drops `nullable`; 3.2 was
  released in September 2025. A finding that holds a 3.0 document to 3.1 rules is wrong.
- **JSON Schema** at the dialect the spec uses, for what a schema keyword constrains and what it leaves open.
- **OWASP API Security Top 10 (2023)** for the security axis, cited by item number.
- **The project's own published spec**: it is the contract. Where the code and the spec disagree, the spec is the
  expectation unless the project says the code is the source of truth, and then the published rendering is.

Style guides (Zalando RESTful API Guidelines, Microsoft REST API Guidelines, Google AIP) are guidance, never
conformance. Cite one only where the project adopts it, or as the source of a recommendation.

Where the project states its own convention in `AGENTS.md`, `CLAUDE.md`, an API guideline document, or a Spectral
ruleset, that wins over the upstream convention. Cite the local rule and note the divergence rather than reporting it
as a defect.

## The contract artifact, first

Before any axis writes a finding, the profile carries one line: **which document is the published contract, and how it
relates to the code.** Everything downstream depends on it.

- **Spec-first or code-first.** Is the spec hand-written and the server (or its stubs) generated from it, or is the spec
  generated from annotations (springdoc, swaggo, FastAPI, NestJS)? In the first case the spec is the promise and the
  code drifts from it; in the second the code is the promise and the committed spec drifts from the code. Each drift has
  a different fix, so say which one applies.
- **Which file, at which version.** One spec per service, a bundled one, or both. Which one consumers download, which
  one generators read, and its `openapi:` and `info.version`.
- **The previous release.** The tag or published artifact that `api-compatibility` diffs against. Without it there is
  no breaking-change review, only a spec review; say so.
- **What sits in front of the server.** A gateway or ingress that enforces authentication, rewrites paths, limits body
  size, or terminates CORS changes which findings are real. Name it, and state which of its rules the review relied on.

## `api-ux`: the operation list is the API

- **One concept, one name.** Enumerate every path segment, parameter, and field name and group by concept. `projectId`
  in one operation and `project_id` or `pid` in another is the most expensive defect on this surface: every generated
  client exposes it, and every caller pays for it on every call.
- **Paths model resources, methods carry the verb.** `POST /users/{id}/delete` beside `DELETE /users/{id}` is two ways
  to do one thing. Collection and item paths follow one pattern throughout.
- **Every parameter and field documents its type, format, unit, default, and allowed values in the schema.** An enum
  that lives only in a validation branch is found by trial and error, and each attempt is a failed request.
- **`operationId` is an identifier a generator turns into a method name.** Missing, duplicated, or unstable ones produce
  `getUsers1` in the SDK. `summary` and `description` are what an agent and a portal reader see; one that restates the
  path teaches nothing.
- **Pagination is designed once.** One parameter vocabulary (`limit` and `cursor`, or `page` and `size`), one response
  shape, a documented maximum page size, and a way to learn there is a next page: an RFC 8288 `Link` header, a
  `next` field, or both. A list endpoint with no pagination returns everything the day the table grows.
- **Response volume.** Defaults return the fields a caller needs; large or nested sub-resources are opt-in
  (`fields`, `expand`, `include`). Measure the response of the five most-called operations on realistic data.
- **Lint with the project's ruleset first, then with a baseline.** Report a lint finding only where it costs a caller:
  a missing `operationId`, an undocumented parameter, an unused or duplicated schema that generators turn into two
  types. A rule violation with no caller consequence is noise.

## `error-model`: what the caller branches on

- **A failure returned as success is the most expensive defect on this surface.** `200` with `{"error": ...}`, `200`
  with an empty body on a lookup that failed, `202` for work that was rejected: every generated client, retry policy,
  and dashboard reads these as success. Enumerate every error path in every handler and the status it produces.
- **One mapping, applied everywhere.** The same condition (validation failure, not found, conflict, permission denied,
  upstream down) produces the same status and the same body shape in every operation. Build the table: condition,
  status per operation, body shape per operation. The rows that disagree are the findings.
- **A stable machine identity.** RFC 9457 `type` is a URI the project controls and documents, or a documented `code`
  extension; `title` and `detail` are prose and free to change. A caller that must parse `detail` to tell "name taken"
  from "name invalid" has no contract.
- **The error body is declared in the spec** for each status the operation can return, including the `default`
  response. A `4xx` with an HTML body from a framework's default error page is a finding on the operations it reaches.
- **Retry semantics are visible.** `503` and `429` with `Retry-After` where the server knows the wait; `409` for a
  conflict a retry will not fix; `500` only for a defect. A client cannot tell "retry" from "stop" when every failure
  is `500`.
- **Partial success.** A batch endpoint reports which items succeeded, which failed and why, with a status that does
  not read as total success (`207` or a `200` whose body says so, documented).
- **Messages name the offending input**: the parameter, the JSON Pointer to the field, the value, and the accepted
  values. Stack traces, SQL, and internal hostnames in `detail` are a `security` finding; note them there.

## `protocol-conformance`: the RFC 9110 obligations

Read the RFC section for each method and status the API uses, and check the code against the `MUST`s:

- **Safe methods do not change state** (§9.2.1). A `GET` that creates, deletes, or increments is reached by
  prefetchers, crawlers, link previews, and retrying proxies.
- **`PUT` and `DELETE` are idempotent** (§9.2.2). A second identical `DELETE` may return `404` or `204`, but must not
  delete something else; a `PUT` that appends to a list, or increments a counter, is not a `PUT`. Clients and proxies
  retry these methods automatically on a dropped connection, which is the trigger.
- **Status codes carry their required headers.** `405` lists `Allow` (§15.5.6); `401` carries `WWW-Authenticate`
  (§15.5.2); `204` and `304` carry no content (§15.3.5, §15.4.5); a `201` identifies the created resource by
  `Location`, or by the target URI when `Location` is absent (§15.3.2); `HEAD` returns the headers `GET` would
  (§9.3.2).
- **Conditional requests** (§13), where the API returns an `ETag`: `If-None-Match` yields `304`, `If-Match` yields
  `412` on mismatch, and weak validators are not used where strong comparison is required (§8.8.3.2).
- **Content negotiation** (§12): an unsupported request `Content-Type` yields `415`, an unsatisfiable `Accept` yields
  `406` or a documented default, and a response that varies by a request header says so in `Vary`.
- **Caching** (RFC 9111): a response that differs per user and lacks `private` or `no-store` can be served to the next
  user by a shared cache. Report the conformance gap here; the exposure belongs to `security`.
- **Problem Details** (RFC 9457): members have the declared types, `status` equals the response status (§3.1.2),
  `type` is a URI reference (§3.1.1), and the media type is `application/problem+json` (§6.1).

## `api-compatibility`: what counts as a breaking change

Breaking, on this surface, means a request that worked stops working, or a response a client parsed changes shape or
meaning. Concretely:

- removing or renaming a path, a method on a path, a parameter, a request field, a response field, or a security
  scheme;
- adding a required parameter or request field, or making an optional one required;
- narrowing a request type: a tighter `pattern`, `maxLength`, `maximum`, a removed enum value, a changed `format`, or a
  new `additionalProperties: false`;
- widening a response type that clients decode strictly: a field that becomes nullable or optional, a new response enum
  value for a generator that emits closed enums (see *Where the sources disagree*), a number that becomes a string;
- changing the status code for an existing condition, the error body shape, or the media type of either;
- changing a default value, a unit, a sort order, a page size, or the meaning of a parameter that keeps its name;
- changing parameter serialization (`style`, `explode`), the authentication scheme, or the scopes an operation needs.

Additive is safe, and the docs should say so: new operations, new optional parameters, new response fields that clients
are told to ignore when unknown.

The diff tool settles the structural half. `oasdiff breaking` against the previous release tag is cheap (see
*Tooling*), and its absence from CI is the mechanism finding the axis file asks for, rated above any single break. The
behavioral half is out of its reach: a changed default applied in code and absent from the spec, a new error mapping,
a page size changed in a constant. Find those by diffing the handlers and the constants between the two tags.

Then settle two questions. **What is the versioning strategy** (path prefix, header, media type, or none), and does the
history follow it: find a breaking change shipped without a new version, and name the release. **Is there a deprecation
path**: `deprecated: true` in the spec, a `Deprecation` and `Sunset` header on the response, and a release in which the
old and new forms both work.

## `contracts`: the spec, the server, and the repository's own clients

- **The spec is a valid machine artifact.** It parses, every `$ref` resolves, and it validates against the OpenAPI
  schema of its declared version. An invalid spec breaks every generator downstream, often silently.
- **Drift in both directions.** Operations, parameters, fields, and status codes the spec declares and the server does
  not serve; and those the server serves and the spec omits. Execute it: run a spec-driven tester against a local
  instance, or validate recorded traffic through a validating proxy.
- **Code-first drift.** Regenerate the spec with the project's own generator and diff it against the committed one.
  A difference means what consumers download is not what the server does.
- **The repository's own clients.** A generated SDK, the frontend's API layer, and internal service clients each encode
  a copy of the contract. Regenerate them, or diff their types against the spec; a hand-written client is checked
  operation by operation.
- **Skew.** During a rolling deployment the new frontend talks to the old backend and the reverse. Name which pairs the
  deployment allows, and check each change for a request one side sends that the other rejects.

## `security`

Authentication declared against enforced is the check that pays most: list every operation with the `security`
requirement the spec gives it (including a global default and any `security: []` override), then call each one without
a credential against a local instance. An operation the spec protects and the server serves is the finding; one the
spec marks public and the server protects is a `contracts` finding. Then object-level authorization (OWASP API1): a
valid credential for tenant A reading tenant B's resource by ID. Mass assignment (API3): a `readOnly` field such as
`id`, `ownerId`, or `role` accepted on write. Unbounded input (API4): request body size, `limit` with no maximum, array
length, decompression ratio, multipart part count. CORS: a reflected `Origin` together with
`Access-Control-Allow-Credentials: true`. Before reporting a missing limit, check the gateway or ingress the profile
names; a limit enforced there is real, but say that the service depends on it.

## `performance`

Count the queries one page of each list endpoint issues, and check whether the count grows with the page size or with
the table. Look for whole-payload buffering on upload and download paths, and for responses built in memory and then
serialized when the framework can stream. Every finding carries a number: queries per request, bytes per response,
milliseconds at a named data size.

## `telemetry` and `observability-operability`

Metrics and spans label the route template (`/users/{id}`), never the raw path; a raw path is one time series per user.
Attribute names follow the OpenTelemetry HTTP semantic conventions (`http.request.method`, `http.route`,
`http.response.status_code`) where the project uses OpenTelemetry. A request ID or trace ID reaches the error body or a
response header, so a caller can quote it. Those belong to `telemetry`. Timeouts belong to `observability-operability`:
a load balancer timeout shorter than the server's lets the server finish work the caller has already abandoned, and a
server timeout shorter than a downstream call's returns `504` for work that completes.

## `tests` and `test-strategy`

`tests` asks whether a documented status code, error type, or header has a test that would fail if it changed, and
whether any test goes through the real HTTP stack, where routing, middleware, authentication, serialization, and error
mapping live. A suite that calls handler functions directly tests none of those. `test-strategy` asks whether the
contract checks sit at the right level: whether a spec-driven test against the server exists at all, whether the e2e
collections duplicate what an in-process test would catch faster, and whether the drift between the spec and the server
has any test that can fail.

## Tooling

Start from the spec and a local instance. Never run a spec-driven tester, a fuzzer, or a mutating probe against a shared
or live environment: Schemathesis sends malformed and destructive requests by design.

```bash
SPEC=api/openapi.yaml                                     # the file the profile named as the contract
npx @redocly/cli lint "$SPEC"                             # validity and $ref resolution
npx @stoplight/spectral-cli lint "$SPEC"                  # with the project's .spectral.yaml when it has one
printf 'extends: ["spectral:oas"]\n' > work/spectral.yaml
npx @stoplight/spectral-cli lint "$SPEC" --ruleset work/spectral.yaml > work/spectral-oas.txt   # the baseline
```

The compatibility diff against the previous release. Check out the whole tag, because a spec split over files resolves
its `$ref`s relative to itself:

```bash
git worktree add work/prev <previous-release-tag>
oasdiff breaking work/prev/"$SPEC" "$SPEC" --fail-on ERR > work/oasdiff-breaking.txt; echo "exit=$?"
oasdiff changelog work/prev/"$SPEC" "$SPEC" > work/oasdiff-changelog.txt
# no local binary: docker run --rm -v "$PWD":/w -w /w tufin/oasdiff breaking work/prev/<spec> <spec>
```

Drift between the spec and the server, against a local instance only:

```bash
schemathesis run "$SPEC" --url http://localhost:8080 --checks all > work/schemathesis.txt
npx @stoplight/prism-cli proxy "$SPEC" http://localhost:8080 --errors   # replay the e2e suite through it
<project generator> && git diff --exit-code -- "$SPEC"                  # code-first: committed spec versus regenerated
```

Then the probes only a hand-written request settles. Read the status line, the headers, and the body together:

```bash
curl -si -X DELETE http://localhost:8080/<item>; curl -si -X DELETE http://localhost:8080/<item>  # same outcome twice
curl -si -X PATCH http://localhost:8080/<collection>                    # 405 with Allow
curl -si http://localhost:8080/<protected-operation>                    # 401 with WWW-Authenticate, problem body
curl -si -X POST -H 'Content-Type: text/plain' --data x http://localhost:8080/<collection>    # 415
curl -si -H 'Accept: application/xml' http://localhost:8080/<item>      # 406 or the documented default
curl -sI http://localhost:8080/<item>                                   # HEAD returns GET's headers, no body
curl -si 'http://localhost:8080/<collection>?limit=1000000'             # is the maximum page size enforced?
```

**The spec is not the server, and the handler is not the stack.** Both gaps generate wrong findings in both directions:

- a defect **observed only in the spec**, or against a mock generated from it (Prism in mock mode), is about the spec;
  whether the server shares it is `inferred` until a request to a running instance shows it;
- a defect **refuted only by a handler-level test** is not refuted: routing, middleware, authentication, and the
  framework's error mapping all run outside the handler, so say what the test skipped and leave the finding standing;
- a defect **observed against the bare server** may be fixed by the gateway in front of it, and one refuted there may
  reappear behind a different gateway. Say which deployment the evidence came from.

Prefer `executed` over `traced`: almost every check in this pack can be settled by starting the server and sending one
request, so a finding about a status code or a header that reasons about the router without calling it should not have
been written that way.

## Where the sources disagree

Do not report a project for picking the other side of a live disagreement. Report it for having no rule, or for
applying two rules in one API.

- **`400` or `422` for a validation failure.** RFC 9110 defines both (§15.5.1, §15.5.21) and does not choose. Report a
  mix, not the choice.
- **`404` or `403` for a resource the caller may not see.** Hiding existence is a legitimate security choice. Report it
  only when it is applied in some operations and not others.
- **Adding a response enum value.** oasdiff and several style guides treat it as breaking, because generators emit
  closed enums; others treat responses as open by contract. It is breaking for this project when a client the project
  ships, or names as supported, decodes the enum strictly. Otherwise it is a recommendation to document extensibility
  (`x-extensible-enum`, or a statement in the spec).
- **Versioning in the path, a header, or the media type.** Each has adherents and none is a standard. Report a missing
  strategy, or a breaking change that bypassed the chosen one.
- **Offset or cursor pagination.** Offset skips and repeats rows under concurrent writes; cursors cannot jump to page N.
  Report a choice that contradicts a documented use case, not the choice itself.
- **RFC 9457 or a house error shape.** RFC 9457 is a format to adopt, not an obligation. A documented house shape used
  consistently is fine; two shapes in one API, or an undocumented one, is the finding.
- **JSON Merge Patch (RFC 7396) or JSON Patch (RFC 6902) for `PATCH`.** Either is correct once declared by media type.
  A `PATCH` that accepts `application/json` with undocumented merge rules is the defect.
- **Field casing.** `camelCase` and `snake_case` are both conventional. A mix inside one API is a finding; the choice is
  not.

## Severity guidance

`CRITICAL` here is an operation reachable without the credential the spec requires, object-level authorization that
lets one tenant read or write another's data, a secret or another user's data in a response or an error body, and a
failure reported as `2xx` on a write that clients then treat as committed. A non-idempotent `PUT` or `DELETE`, a `GET`
with side effects, an authenticated response cacheable by a shared cache, and a breaking change shipped in a minor
release with no diff gate are `HIGH`. Spec-versus-server drift, one condition mapped to different statuses across
operations, and a list endpoint with no enforced maximum are `MEDIUM`, rising to `HIGH` where a shipped client already
fails on the drift. Missing headers that no caller in the profile reads, and lint findings with a caller consequence,
are `LOW`.

## Architectural questions this surface raises

For the `architecture` distiller, not for the evidence axes:

- Which artifact is the source of truth, the spec or the code, and does the build enforce it in the direction it
  claims?
- Do the operations model what callers are trying to do, or the tables underneath? How many calls does the most common
  task take?
- Where the same contract is encoded several times (spec, server, generated SDK, frontend client, e2e collections), how
  many of those copies does a field rename have to pass through, and which of them would catch the miss?
- What compatibility window does the API promise, to whom, and what in CI enforces it?
- Which concerns does the service delegate to the gateway in front of it (authentication, limits, CORS, rate
  limiting), and does the service still hold when deployed behind a different one?
- Does the error model give callers the identities they need to automate recovery, or does every client parse prose?
