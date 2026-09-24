# Surface pack: Model Context Protocol server

Apply this pack when the repository ships an MCP server: a stdio binary a client launches as a subprocess, a Streamable
HTTP endpoint, a wrapper that re-exports an existing CLI or REST API as tools, or a library whose product is the tool
list it registers. It also applies to the MCP half of a repository whose main product is something else — a CLI that
ships an `mcp` subcommand has two surfaces, and this pack covers one of them. It does not apply to an MCP *client* or
host: the client-side concerns (consent UI, sandboxing, tool filtering) are a different review, and most of this file
would be answering questions nobody asked.

The caller is a language model that never sees your README. It reads `tools/list` — names, descriptions, JSON Schema —
and decides from that alone. It cannot ask a clarifying question, it pays for every byte of every result in context, it
retries on any error whose text suggests a retry might work, and it will call a destructive tool if the description
reads like the safe one. Behind it sits a host application that decides which of your tools even reach the model, and a
human who approves or denies the call from a one-line summary. Design that survives all three is the subject of this
pack.

A surface pack is a lens, not an axis. Several axes read this file, so **it says who owns what** — stay inside your row
of the table below and leave the rest alone. A concern raised twice in two vocabularies costs the reader more than it
costs you.

## Ownership

| Concern | Owner axis |
| --- | --- |
| Tool inventory: granularity, overlap, whether a tool models a workflow or a REST endpoint; names and namespacing; `description` and parameter descriptions as the only documentation the model gets; `inputSchema` legibility — required versus optional, enums, defaults, units, `additionalProperties`; `outputSchema` presence and fidelity; result volume, truncation, pagination, and the flag that lifts a cap; empty states; naming of returned fields | `api-ux` |
| `isError: true` versus a JSON-RPC error, and which conditions map to which; the stability and documentation of any machine-readable error identity the server returns; message shape and whether it tells the model what to do differently; partial success in batch tools; what a call against an expired or unknown handle returns; timeouts and what the caller sees when one fires | `error-model` |
| Conformance to the protocol revision the server claims: required fields, capability declaration, pagination cursors, cancellation, progress, transport framing, header and body agreement on HTTP, behavior on an unknown method or an unsupported version, and interoperability with clients one revision older | `protocol-conformance` |
| Renaming or removing a tool, argument, or output field; tightening a schema; changing a default, a unit, or the meaning of an argument; changing which conditions produce an error; dropping a protocol revision; changing the shape of `structuredContent`; deprecation windows and how a client learns | `api-compatibility` |
| Drift between the declared schema and the code that reads the arguments; arguments accepted but undeclared, or declared but ignored; `outputSchema` that the results violate; validation that the handler skips because the transport already "validated"; idempotency of mutating tools; whether `annotations` match what the tool actually does | `correctness` |
| Tool descriptions and results as an injection surface; secrets in arguments, in results, or in logs; token audience validation and passthrough; SSRF in anything that takes a URL; authorization on state handles; consent gates and what bypasses them; what a compromised or malicious caller reaches through the tools | `security` |
| Where the server logs and whether that channel is safe on this transport; progress on long calls; timeouts and cancellation actually stopping work; per-call latency and cost; trace context propagation; what an operator sees when a tool fails in production | `observability-operability` |
| Agreement between the README, the install snippet, the registry entry, and what the server actually registers; the configuration a user must supply before the first call succeeds; whether a tool that needs setup says so in its description rather than only in the README | `docs-onboarding` |
| A test that asserts the tool list (names, schemas) so a rename shows up in review; a test per documented error condition; schema-validity tests; tests that call the server over its real transport rather than the handler function | `tests` |
| Which protocol revision the server targets, how far behind the current one it sits, what that costs its callers today, and whether the SDK it depends on can reach a newer one at all | `dependencies` |
| Startup latency per process on stdio, the runtime the user must install, packaging and registry publication, and the version the server reports | `build-release` |
| Concurrent calls on one connection or process, cancellation mid-call, shutdown on closed stdin, long-lived streams, and any state shared between calls | `concurrency-lifecycle` |

## Normative sources

Fetch these rather than recalling them; the expectation in a finding must cite a section, not a memory. MCP moves
faster than model training data, and a finding that holds the server to a revision it never claimed is noise.

- **The MCP specification, at the revision the server implements.** `modelcontextprotocol.io/specification/<date>`.
  Revisions to date: `2024-11-05`, `2025-03-26`, `2025-06-18`, `2025-11-25`, `2026-07-28`. Establish which one the code
  targets — the SDK version pins it — before you write a single finding, and read that revision's pages, not the
  `latest` alias.
- **The schema for that revision** (`schema/<date>/schema.ts` in the `modelcontextprotocol/modelcontextprotocol`
  repository) is the source of truth for field names, optionality, and documented defaults. Quote it rather than the
  prose page when the two could be read differently.
- **The revision's changelog page.** It is the fastest way to see what the server would have to change to move up, and
  what a client one revision older will not understand.
- **JSON-RPC 2.0** for the error object, reserved codes, and the notification rules.
- **JSON Schema 2020-12** — the default dialect when a schema carries no `$schema`.
- **Security best practices** (`/specification/<date>/basic/security_best_practices`) for confused deputy, token
  passthrough, SSRF, and state-handle hijacking, and **`/basic/authorization`** for anything HTTP-based.
- **Anthropic, "Writing effective tools for AI agents"** — the design guidance the specification deliberately leaves
  out: tool consolidation, namespacing, semantic field names, response-format control, and evaluation-driven design.
  Cite it as guidance, never as conformance.
- **Client best practices** (`/docs/<date>/develop/clients/client-best-practices`) — how hosts ration context across
  servers. It constrains server design more than most server authors realize; see the token-cost bullets below.
- **The SDK's own documentation and source.** What the SDK fills in for you — capability declaration, schema
  generation, error mapping, argument validation — decides which of the checks below can even fail in this codebase,
  and a finding that blames the server for something the SDK guarantees will be rejected.

Where the project states its own convention in `AGENTS.md`, `CLAUDE.md`, or a design document, that wins over the
upstream convention — cite the local rule and note the divergence rather than reporting it as a defect.

## The revision question, first

`2026-07-28` is not a bigger `2025-11-25`. It removed the `initialize` handshake and made every request carry its own
protocol version and client capabilities in `_meta`; it removed protocol-level sessions and the `Mcp-Session-Id`
header; it replaced server-initiated requests (sampling, elicitation, roots) with the multi round-trip pattern, where
the server returns `resultType: "input_required"` and the client retries the original call; it added `server/discover`,
required `resultType` on every result, and moved tasks into an extension; it deprecated roots, sampling, and logging
outright.

So the first artifact this surface produces is one line in the profile: **which revision, established from the SDK
version and the wire, not from the README.** Everything downstream depends on it.

- A server on `2025-06-18` or `2025-11-25` is not defective for using `initialize`, sessions, or `logging/setLevel` —
  those are that revision's protocol, and holding it to `2026-07-28` is a conformance finding that is simply wrong.
  Being behind is a finding of its own kind; see below.
- A server that claims `2026-07-28` and still infers anything from connection identity — a session, a client version, a
  negotiated capability cached at handshake — is defective on `protocol-conformance`, and the failure is invisible
  until a client interleaves two conversations on one process.
- A server that advertises one revision and behaves as another is the finding worth hunting: the version string in
  `serverInfo` or the `MCP-Protocol-Version` it accepts, against the fields it actually requires and emits.

### Falling behind is a finding — write it once, with the cost in it

**Raise exactly one finding for a stale revision**, owned by `dependencies`, and let every axis that trips over a
consequence add a cross-axis line pointing at it instead of raising its own. The claim is not "the version is old"; a
reviewer who writes that has produced a changelog diff. The claim is what this server's callers cannot do, or what its
maintainers will pay, because of where it sits — so state the current revision, the one the code targets, the gap in
revisions, and then the concrete consequences from the list below. Anything you cannot tie to a consequence goes
unreported.

What each step actually buys, so the finding can name it:

- **`2024-11-05` → `2025-03-26`:** Streamable HTTP replaces HTTP+SSE (now Deprecated under the feature-lifecycle policy
  and eligible for removal), the OAuth 2.1 authorization framework, tool annotations, audio content, `completions`.
- **`2025-03-26` → `2025-06-18`:** structured tool output (`outputSchema` and `structuredContent`), elicitation,
  resource links, the `MCP-Protocol-Version` header, servers classified as OAuth resource servers with protected
  resource metadata, the security best practices page, `title` separated from `name`. JSON-RPC batching is removed.
- **`2025-06-18` → `2025-11-25`:** tasks for long-running work, icons, tool calling in sampling, OpenID Connect
  discovery, richer elicitation enums.
- **`2025-11-25` → `2026-07-28`:** statelessness, `server/discover`, MRTR, caching hints (`ttlMs`, `cacheScope`),
  deterministic tool order, the error-code allocation policy. Roots, sampling, logging, and Dynamic Client Registration
  enter deprecation.

Severity comes from the consequence, not the distance:

- `HIGH` when the gap costs security or reachability today: a server still on HTTP+SSE, or one predating the
  `2025-06-18` rules that made audience validation and resource indicators explicit, or a revision the clients this
  project names have already dropped.
- `MEDIUM` when it costs the caller a capability the tools visibly need — most often a pre-`2025-06-18` server whose
  tools return structured data with no `outputSchema` to declare it, or a long-running tool with no tasks to hang it
  on. Say which tool, and what the model does instead today.
- `LOW` when nothing breaks and nothing is missing: the server works, its clients support it, and the cost is
  maintenance drift. Still worth one line, because the `2026-07-28` rewrite is large enough that the price of the move
  rises with every revision skipped.

Two things make this finding useful rather than a nag. **Name the migration cost**, at least coarsely — an SDK bump and
a handful of call sites, or a rewrite of everything that assumed a session. And **check the SDK before blaming the
code**: where the server's SDK does not yet implement a newer revision, the finding belongs to the dependency and its
release cadence, and the recommendation is to track it, not to hand-roll the protocol.

## `api-ux` — the tool list is the API

- **Tools model workflows, not endpoints.** A server that exposes one tool per underlying REST call makes the model
  reassemble a workflow it cannot see: `list_users` plus `list_events` plus `create_event` costs three turns and two
  chances to pick the wrong ID, where `schedule_event` costs one. The falsifiable version of this finding is a
  transcript, not an opinion — run a realistic task and count the calls that exist only to feed the next call.
- **Names are guessed by analogy.** Predictable verbs (`search`, `get`, `create`, `update`, `delete`, `run`), one
  grammar throughout, and a consistent namespace prefix per server (`asana_search`, `asana_projects_search`) so a host
  aggregating a dozen servers does not collide. The specification constrains the character set and length; it says
  nothing about legibility, which is where the cost is.
- **The description is the documentation, and it is read once per session by a reader who cannot ask.** It states what
  the tool does, when to reach for it rather than its neighbor, what it costs, and what it will not do. Ambiguity
  between two tools is paid on every task; write the sentence that distinguishes them or merge them.
- **Every argument carries a description, and enums carry their values.** A `string` parameter whose accepted values
  live only in a validation branch is discovered by trial and error, and each attempt is a turn. State units, formats,
  and defaults in the schema, not in the README. Prefer `user_id` over `user` when an ID is what you mean.
- **The schema is legible to a machine, not merely valid.** `required` reflects what the handler actually needs;
  optional arguments have real defaults; `additionalProperties: false` where the handler ignores extras; no network
  `$ref`; no composition-keyword thicket (`anyOf` of `oneOf` of `allOf`) that a model has to unify to see that two
  fields are mutually exclusive — say it in the description as well. A tool with no parameters still declares an object
  schema.
- **`outputSchema` is not optional in practice.** Hosts that generate typed APIs for code execution fall back to `any`
  without it, and a model reading an untyped blob re-derives the shape on every call. Where the tool returns structured
  data, the absence of an output schema — and any drift between it and the real result — is the highest-value finding
  this axis produces on this surface.
- **Result volume is a first-class cost, and it is paid twice.** Once in the tool list on every session, once per call.
  Measure both: the byte and token size of `tools/list`, and of the ten most likely calls. Defaults carry the fields a
  caller needs rather than the row the database returned; identifiers a model cannot use (`uuid`, `mime_type`,
  `256px_image_url`) are noise unless another tool consumes them; long results truncate with a size hint and the
  argument that lifts the cap; totals are pre-computed; an empty result says so explicitly, because an empty string is
  indistinguishable from a crash. For scale: Claude Code caps a tool response at 25,000 tokens, and Anthropic's own
  example cut a Slack result from 206 tokens to 72 by offering a `response_format` of `concise` or `detailed`.
- **The tool list has a context budget you do not control.** Hosts switch to progressive discovery once definitions
  reach roughly 1–5% of the context window, and then your tool is found by search over its name and one-line
  description, or not at all. A forty-tool server with prose descriptions is a design decision about discoverability;
  say whether the project made it deliberately.
- **Annotations describe behavior a caller cannot infer** — `readOnlyHint`, `destructiveHint`, `idempotentHint`,
  `openWorldHint`. Note the documented defaults before reporting anything: absent means `readOnlyHint: false`,
  `destructiveHint: true`, `idempotentHint: false`, `openWorldHint: true`. They are hints, and clients are told not to
  trust them from untrusted servers, so their absence is a recommendation. An annotation that contradicts the code is a
  defect, and it belongs to `correctness`.

## `error-model` — what the model branches on

- **A failure returned as success is the most expensive defect on this surface.** A result with `isError` unset, or
  absent, whose text says "error: not found" reads to the client as a completed call; the model summarizes the failure
  as a fact and moves on, and the wrong answer surfaces three turns later as something else. Enumerate every return
  path in every handler and check which ones set the flag. This is the MCP analogue of `exit 0` on failure, and it
  earns the same severity.
- **The split is deliberate, so hold the server to it.** Tool execution errors — validation, business rules, upstream
  failures — go in the result with `isError: true`, because the client is told to show those to the model so it can
  self-correct. Failures in *finding* the tool, malformed requests, and unsupported operations go back as JSON-RPC
  errors, which the client may withhold. A server that maps every exception to a protocol error hides recoverable
  failures from the only party that could fix them; one that maps everything into `isError` makes an unknown tool look
  like a business rule.
- **Error codes: the number space is allocated, and the allocation is recent.** `-32700` and `-32600` to `-32603` are
  JSON-RPC's. Under `2026-07-28`, `-32000` to `-32019` is legacy — grandfathered for existing SDK usage, closed to new
  codes — and `-32020` to `-32099` belongs to the specification (`-32020` `HeaderMismatch`, `-32021`
  `MissingRequiredClientCapability`, `-32022` `UnsupportedProtocolVersion`). New application codes go outside
  `-32768`–`-32000` entirely. A server minting its own meaning for `-32001` is following the old convention, not
  breaking the new rule, unless it claims `2026-07-28`; a server emitting a reserved code with its own meaning is
  defective at any revision. Note also that resource-not-found moved from `-32002` to `-32602`.
- **Tool errors need a stable identity too, and the protocol gives you none.** `isError` is a boolean; everything else
  is prose the model reads and a client cannot branch on. Where the project needs callers to distinguish "expired
  handle" from "no permission" from "upstream is down", that identity has to be designed — a `code` field in
  `structuredContent` under a documented `outputSchema` is the honest place for it. Report the absence only where
  something actually branches; report a *documented* identity that the code does not emit consistently in every case.
- **The message tells the model what to do differently.** Reason, then the corrective action, naming the offending
  argument and its accepted values: "Invalid `departure_date`: must be in the future; today is 2026-08-14." A stack
  trace, an upstream vendor code, or "an error occurred" spends a turn and buys nothing. Give an example of a
  well-formed argument where the format is the problem.
- **Retry semantics have to be visible.** A model retries anything that sounds retryable. Say when it is pointless
  ("this project has no issues" is not a transient failure), and make sure a tool that retried internally does not
  report the last attempt's error as though it were the first.
- **Partial success in anything batched.** Which items succeeded, which failed and why, and a flag that does not read
  as total success. A batch tool that returns the first failure and abandons the rest forces the model to re-derive
  what happened.
- **Expired and unknown handles.** Where the server keeps state across calls behind an identifier, a call with a stale
  one must say so explicitly, so the model can create a new one instead of concluding the data is gone.

## `protocol-conformance` — the wire, at the claimed revision

Read the revision's schema and check the fields the code emits and requires against it. The checks that pay:

- **Capability declaration matches reality.** A server that declares `listChanged` and never notifies, or notifies
  without declaring, breaks client caching in opposite directions.
- **`tools/list` is complete, and stable in the way the revision requires.** Pagination honored to the last cursor; at
  `2026-07-28` also a deterministic order (a `SHOULD`, so clients may cache) and no variation by connection. A server
  that pages by an in-memory offset instead of an opaque cursor drops or repeats tools when two clients page
  concurrently.
- **The transport rules, which are absolute on stdio.** Anything written to `stdout` that is not a JSON-RPC message
  corrupts the stream: a print statement in a handler, a library that logs to stdout, a banner at startup, a warning
  from the runtime. Logs go to `stderr`. Messages carry no embedded newlines. The server exits when stdin closes.
- **On HTTP:** the `Origin` header is validated (403 on mismatch), the local bind is loopback rather than `0.0.0.0`,
  and at `2026-07-28` the required headers agree with the body or the request is rejected with `-32020`. A server that
  routes on a header and executes on the body is the vulnerability that rule exists to prevent.
- **Cancellation and progress do what they claim.** A cancelled request stops work and sends nothing further; a
  progress token that is accepted and never used leaves the caller staring at a blank stream.
- **Interoperability with the neighboring revision.** What happens when a client one revision older connects — a clear
  version error, or a confusing failure ten fields later? This is where a compatibility matrix in the docs is worth
  more than any single fix.

## `api-compatibility` — a published tool list is a frozen contract

Breaking, on this surface, means a call the model would have made stops working, or a result the caller parsed changes
shape. Concretely: renaming or removing a tool or an argument; making an optional argument required; narrowing an enum
or a type; changing a default, a unit, or the semantics of an argument that keeps its name; changing which conditions
produce `isError`; renaming or removing a field in `structuredContent`; changing the shape of an untyped text result
that consumers have learned to parse; dropping support for a protocol revision.

Additive is safe and the docs should say so: new tools, new optional arguments, new output fields consumers are told to
tolerate.

Two questions this axis must settle explicitly. **Is the text result a contract?** If nothing says otherwise, callers
parse it and it is one in practice; the fix is a documented `outputSchema` and structured results, not a promise never
to touch the prose. And **is there a deprecation path at all** — a tool that keeps working while its description says
what replaced it, for at least one release, rather than disappearing between two patch versions of an npm package that
users install with `@latest`. A renamed tool is worse than a removed one: the model does not fail, it picks the nearest
survivor.

## `correctness` — the schema versus the handler

Drift in both directions: declared and ignored, accepted and undeclared. Walk each handler against its schema and check
what it reads out of the arguments object. Constraints that exist only in the schema (`minimum`, `pattern`, `enum`) are
enforced by the client at best and by nobody at worst — the server validates its own inputs, or a direct JSON-RPC call
walks straight past them. Where the SDK validates, say so and move on; where it validates only the top level, the
nested object is yours.

Then: `structuredContent` that violates the declared `outputSchema` on some branch (the empty case and the error case
are where it happens); annotations that contradict the code (`readOnlyHint: true` on a tool that writes is the one to
hunt); a mutating tool that is not idempotent and does not say so; a tool whose result depends on state left by a
previous call, on a protocol that guarantees none.

## `security`

- **The tool list is an injection surface.** Descriptions and schemas are instructions the model reads before it reads
  the user. Where any part of a description, an enum, or a tool name is built from data the server does not control —
  a database row, an upstream API, a file in the repository being indexed — that is an injection path, and it is the
  first thing to look for. The same applies to results: a tool returning attacker-controlled text into the model's
  context is the documented mechanism behind tool poisoning.
- **Secrets.** Tokens in tool arguments end up in host logs and in the model's context; environment or a credential
  file is the answer. Check what results and error messages echo — connection strings, `Authorization` headers,
  internal hostnames — and what the server writes to `stderr` at debug level.
- **Authorization on every call, including handles.** MCP has no session to authenticate. A state handle is a name, not
  a capability: the server validates the caller against it on every call, keys stored state by the verified identity,
  and generates handles with real entropy. Possession is not authentication.
- **HTTP servers: audience validation.** Accepting a token that was not issued for this server, or forwarding a client
  token unchanged to a downstream API, is the token-passthrough anti-pattern the specification forbids outright. Check
  the audience claim is verified, and check what the server sends downstream.
- **SSRF and reachability.** Any tool taking a URL, a host, or a file path is a request generator with the server's
  network position and file access. Loopback, link-local (`169.254.169.254`), and private ranges; redirects; path
  traversal out of the configured root.
- **What a destructive tool can reach without a human.** Hosts auto-approve on `readOnlyHint`, and users approve
  repeated calls once. Assume every tool will eventually be invoked without a human reading the arguments, and judge
  the blast radius on that assumption.

## `observability-operability`

Logging goes where the transport allows: `stderr` on stdio, and never `stdout`. Long calls report progress or the host
shows nothing for ninety seconds. Timeouts are the server's job as much as the client's — an upstream that hangs holds
the caller's turn open. Trace context arrives in `_meta` (`traceparent`, `tracestate`, `baggage`) under the
OpenTelemetry conventions; a server that drops it breaks the operator's ability to connect a slow agent turn to the
query behind it. And the operational question specific to stdio: one process per client, started and killed by the
host, with no place to expose metrics — say how the project expects to be observed at all.

## `docs-onboarding`

The README's install snippet, the client configuration JSON, the registry entry, and the tools the server registers are
four renderings of one contract; diff them, and the pairs that disagree are the finding. A tool that fails until an
environment variable is set says so in its own description, because the model never reads the README. Where the server
is published to the MCP registry, the `server.json` name, version, and package coordinates are part of the same
contract. Check that the documented example calls actually run — an example that no longer works costs more than a
missing one, because the model trusts it.

## `tests`

The tool list is a snapshot test: names, argument names, required flags, and enum values, so a rename shows up in
review rather than in someone's agent transcript. A test per error condition asserting both the channel (`isError`
versus JSON-RPC) and the identity. A schema-validity test — every `inputSchema` and `outputSchema` compiles under
2020-12 and every example result validates against its output schema. At least one test that speaks the real transport
rather than calling the handler function directly, because framing, argument coercion, and error mapping all live in
the layer a direct call skips. Note honestly whether the suite tests the protocol or only the business logic behind it;
on this surface the protocol is the product.

## Tooling

Get the inventory first — every check above reads from it. Use the SDK's own client or the Inspector in CLI mode, and
match the tool version to the server's revision; an Inspector that speaks a different era will produce failures that
belong to the harness.

```bash
npx @modelcontextprotocol/inspector --cli <server-cmd> --method tools/list > work/tools.json
jq -r '.tools[] | "\(.name)\t\(.description | length)\t\(.inputSchema | tostring | length)"' work/tools.json
wc -c work/tools.json                                   # the per-session cost, before any call
npx @modelcontextprotocol/inspector --cli <server-cmd> --method tools/call \
  --tool-name <tool> --tool-arg key=value | jq '{isError, structuredContent}'
```

Then the checks that only a hand-written request settles. On stdio, drive the server with newline-delimited JSON-RPC on
stdin and read `stdout` byte for byte — that is the only way to catch a stray print. On HTTP, `curl` the endpoint with
and without `Origin`, with a mismatched protocol-version header, and with an unknown method, and read the status code
and the JSON-RPC error together.

Two measurements turn opinion into evidence. **Size**: bytes and tokens for `tools/list` and for the ten most likely
calls, against the raw material each call summarizes — a wrapper that costs more than reading the file it wrapped has
cancelled its own reason to exist. **A transcript**: give a fresh agent three realistic tasks and nothing but this
server, and record every wrong tool choice, every schema the model got wrong on the first try, every result it had to
call twice to understand. That transcript is the strongest evidence this surface can produce, and no amount of reading
the handler will give you it.

Prefer `executed` over `traced` here: every claim in this pack can be settled by starting the server and calling it, so
a finding that reasons about a schema without invoking the tool should not have been written that way.

## Where the sources disagree

Do not report a project for picking the other side of a live disagreement. Report it for having no rule.

- **How many tools, and how coarse.** Anthropic's guidance is to consolidate around workflows; hosts have answered the
  same problem with progressive discovery, which lowers the price of a large catalog. Neither settles a number. What is
  reportable is a catalog nobody has measured, or overlapping tools with no rule for which to reach for.
- **Duplicating `structuredContent` into a text block.** The specification says a tool returning structured content
  should also return the serialized JSON as text, for older clients. That doubles the tokens on every call. A project
  that skips it deliberately, having stated which client versions it supports, has made a defensible choice; one that
  does it without knowing is paying twice for nothing.
- **Result format.** JSON, Markdown, or a compact table — there is no consensus and the sources say so. Judge it
  against measurements the project made, not against your preference.
- **Annotations.** Useful to hosts, untrusted by design. Absence is a recommendation; a contradiction is a defect.
- **Error identity inside `isError` results.** The specification defines none, so a project inventing a `code` field is
  not conforming to anything — and a project with nothing is not violating anything either. The question is whether the
  callers of this server need to branch, and whether the answer was chosen or defaulted into.

## Severity guidance

A failure reported as success — `isError` unset on an error path — is the `CRITICAL` path here, together with a
destructive tool annotated `readOnlyHint: true`, a token accepted without audience validation, and a secret returned in
a tool result. `HIGH` covers a state handle usable by any caller who guesses it, non-JSON on `stdout` breaking a stdio
session, an unvalidated `Origin` on a locally bound HTTP server, and a tool description assembled from untrusted data.
Schema-versus-handler drift, a missing `outputSchema` on a tool returning structured data, and two tools whose
descriptions do not distinguish them are `MEDIUM` — each costs every caller a wasted turn. Result verbosity is `LOW`
until it is measured; with numbers across the calls a caller actually makes, it earns `MEDIUM`. A stale protocol
revision is rated by what the gap costs, not by its size — see *Falling behind is a finding*.

## Architectural questions this surface raises

For the `architecture` distiller, not for the evidence axes:

- Does the tool list model what a caller is trying to accomplish, or the API that happened to be underneath?
- Where a CLI, a library, and this server all exist, is the contract shared or re-implemented per entry point — and
  which of the three does a behavior change have to pass through today?
- Should some of this be resources or prompts rather than tools? Data the model reads is not the same as an action it
  takes, and a server that has only tools may be paying for that.
- What is the intended context budget for this server, and who owns it as the catalog grows?
- Which protocol revision is the project committing to, when will it move, and what breaks for users when it does?
- Is anything in CI enforcing the tool contract, or does the model find out first?
