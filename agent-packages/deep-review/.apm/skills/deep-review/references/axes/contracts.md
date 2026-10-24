# Axis: internal contracts

Finding prefix: `CTR`.

Where two components of this repository meet, do the producer and the consumer agree? Check them at this commit, and
across the version skew a deployment allows. A monorepo compiles each component against its own idea of the other.
A server can drift from its spec, and a client from both. A worker can read a field the enqueuer stopped writing, or a
binary can read an environment variable the chart never sets. Each side passes its own tests. The defect lives only
in the pair, so this axis reviews pairs, never one side alone.

**A seam** is one contract between one producer and one consumer, both shipped from this repository: an endpoint
group, a message type, a table, a config key, a shared enumeration. Where the run gives you a list of seams instead
of paths, that list is your scope. Otherwise you build it first (Method, step 1).

## What counts as a finding

The expectation source is the contract artifact (the spec, the schema, the message type, the chart value) where one
exists. Where none exists, the producer's actual behavior is the source and the consumer must match it. Where neither
side is authoritative, the disagreement is still the defect: name both candidates for the fix.

- **Spec against server.** A route, a method, a status code, a required field, an enum value, a content type, or an
  error body that the spec declares and the server does not implement, or the reverse. An extra undeclared route is
  a finding only when a client in this repository calls it.
- **Spec or server against a client.** A generated client built from an older spec than the one committed, a
  hand-written client in another language that sends a field the server does not read, omits one it requires,
  expects a status code the server never returns, or parses an error body the server does not emit.
- **Message and job payloads.** The enqueuer writes a shape the consumer does not decode: a renamed field, a changed
  type, a field the consumer requires and the producer marks optional, a queue or topic name spelled differently on
  each side. Delivery semantics count too: the consumer assumes ordering or exactly-once that the producer and the
  broker configuration do not provide.
- **Shared storage.** One component writes a table, a key prefix, a bucket layout, or a cache entry, and another
  reads it with a different meaning: an enum value the reader does not know, a nullable column the reader treats as
  required, a unit or time zone that differs, a soft-delete flag one side honors and the other ignores.
- **Configuration keys.** A key the chart, compose file, or manifest sets and the binary never reads, or the binary
  reads and nothing sets. Also a port, path, service name, or header that one side assumes and the other declares
  differently. Defaults count: a binary whose default port differs from the port the chart's probe targets.
- **Duplicated domain logic.** Two implementations of one rule in different components or languages: a
  classification, a validation, a normalization, a version comparison, a breaking-change detector. They disagree on
  an input both accept. The two must agree because some caller combines their outputs or shows them to one user;
  name that caller.
- **Version skew.** Components that are released or rolled out independently, where the old consumer meets the new
  producer (or the reverse) during an upgrade the project supports, and the pair fails: a new required field, a
  removed enum member, a renamed queue, a new message version the old consumer rejects or silently drops.

## What is not a finding

- A spec field, an endpoint, or a config key that no consumer in this repository uses. That is dead surface; mention
  it under *Cross-axis notes* for `api-compatibility` or `deployment-config` if it matters to them.
- A mismatch on a path the consumer never takes. Trace the call before you report; a disagreement nobody reaches has
  no consequence.
- A tolerant reader ignoring an extra field. That is the reader working as designed.
- Two implementations that differ on inputs outside the domain either one accepts.
- Skew that the project's documented upgrade order excludes. An order that exists nowhere in writing does not
  exclude anything: the skew is then in scope, and the missing order is part of the finding.
- A spec that is valid but badly styled, an HTTP status code that is unconventional but agreed by both sides. Those
  belong to `api-ux` and `error-model`, per `surfaces/rest-http.md`.

## Method

1. **Build the seam list.** Find the contract artifacts: spec files, generator configs, message type definitions,
   queue and topic name constants, table names that appear in more than one component, environment variables in
   charts and compose files, and enumerations that appear by name in two languages. For each seam, name the producer
   and the consumer by component and `path`, and the release unit each one ships in (image, chart, package). Two
   components in one release unit have no skew; two units with separate versions do.
2. **Diff names first.** These checks are cheap and mechanical. Grep config keys on both sides and diff the sets.
   Extract enum members from each side and diff them. Collect queue, topic, table, and header names from each side
   and diff those too. Keep each script and its output under `work/contracts/`.
3. **Diff the API surface against the spec.** Extract routes and methods from the router registration (or the
   framework's route dump) and diff them against the spec's paths. Regenerate each generated client from the
   committed spec in your worktree and diff the result against the committed client. A non-empty diff means the
   client in use is not the client the spec describes.
4. **Validate real payloads against the schema.** Recorded responses, e2e fixtures, Postman collections, snapshot
   tests, and example messages are payloads somebody captured. Validate them with a schema validator for the spec's
   format and version. Run the existing contract tests (Pact, schema tests, consumer-driven suites) and record the
   result.
5. **Run duplicated logic side by side.** Build a shared input set: the fixtures of both implementations, plus the
   boundary cases from either one's tests. Feed it to both, diff the outputs, and report each disagreement with its
   input. This step settles more than any amount of reading.
6. **Replay across skew.** For each seam that crosses release units, take the producer's payload or schema from the
   previous release tag (`git show <tag>:<path>`) and feed it to the HEAD consumer, then the reverse. Where a test
   harness exists, do it in a throwaway test. Otherwise trace the decoder against the old shape. Running the
   upgrade itself belongs to `upgrade-migration`; you establish which pairs are incompatible.

Executed comparisons beat reading. A seam you only read is `traced` at best; say so in the table.

## Required section

End the report with **Seams**, one row per seam, including the seams that came out clean:

| Seam | Producer (`path`) | Consumer (`path`) | Contract artifact | Release units | How checked | Result |
| --- | --- | --- | --- | --- | --- | --- |

`How checked` names the command, script, or test, or says `read` where nothing ran. `Result` is `agree`, a finding
id, or `not checked` with the reason. When you cover only a slice, list the seams that cross its boundary and mark
the other side as outside your slice. A seam that crosses two slices belongs to the slice holding the consumer; the
other slice lists it and marks it so. A seam missing from this table is a seam nobody looked at; synthesis axes and
the consolidator read the table for exactly that.

## Severity

- A silent disagreement is worse than a loud one. A consumer that drops a field, misclassifies a value, or reads a
  default where the producer wrote data corrupts results without any error: `HIGH`, or `CRITICAL` when it reaches
  persisted user data.
- A disagreement that fails at startup or on the first request is `MEDIUM`: the first deploy reveals it.
- A skew failure inside a supported upgrade window rates as its consequence during that window. Where the window is
  short and the failure is a retry, it is `MEDIUM`. Where messages are dropped or rows are written wrong, it is
  rated as the silent case.

## Ownership

The line with `api-compatibility`: if both the producer and the consumer ship from this repository, including
components on separate release trains, the seam is yours. If the consumer lives outside the repository, the seam is
theirs. The same spec can be both: whether the server matches the spec at HEAD is yours; whether the spec changed
incompatibly since the last release is theirs.

| Concern | Owner axis |
| --- | --- |
| Producer and consumer in this repository disagree at HEAD, or across skew between its own release units; a config key, port, or service name the chart and the binary must both agree on; two components reading one schema with different meanings; a client that parses an error body the server does not emit; two implementations of one rule disagreeing | `contracts` |
| A change to a published contract that breaks consumers outside the repository; versioning and deprecation policy | `api-compatibility` |
| Conformance to an external standard or a peer this repository does not own | `protocol-conformance` |
| Whether a test pins a seam, and what kind of test it should be; a missing contract test with no drift found | `test-strategy` |
| Chart and manifest correctness in general: rendering, probes, RBAC, resources | `deployment-config` |
| Migrations, their ordering and reversibility, durability of stored data | `data-lifecycle` |
| Executing the upgrade, rollback, and mixed-version run | `upgrade-migration` |
| What an error body means and whether a caller can act on it | `error-model` |
| HTTP naming and OpenAPI style | `api-ux` |
| Which status code and error body a condition gets | `error-model` |
| RFC 9110 and RFC 9457 obligations | `protocol-conformance` |
| A defect inside one implementation of duplicated logic; a consumer's idempotency under the duplicates the producer does send | `correctness` |
| Whether the logic should be duplicated at all | `architecture` |
| Whether an internal call is authenticated and authorized | `security` |
