# Axis: API and ABI compatibility

Finding prefix: `COMPAT`.

What this code has promised to people who already depend on it, and what it will cost to change. Judge both the
current state and the mechanism: a repository with no compatibility mechanism will break its consumers eventually
regardless of how careful the last commit was.

## Surfaces

**What counts as a breaking change is decided by the form, not by this file.** Adding a required field to a CRD, to a
REST response, to a protobuf message, to a Kafka payload, and to a Java interface are five different events with five
different blast radii. Read `references/surfaces/<form>.md` for each form this repository exposes: the pack states the
breaking-change rule, the normative source, and the diffing tool for that form, and its ownership table marks which
concerns are yours.

Compatibility is not only the source API. Inventory every surface a consumer can depend on:

- source and binary API (signatures, generics, exceptions, default methods, sealed hierarchies);
- serialized forms: wire messages, persisted files, database schemas, cache entries, `Serializable` classes;
- configuration: property names, environment variables, defaults, and the meaning of a default;
- observable behavior consumers rely on: ordering, timing, thread of callback invocation, error types;
- extension points: interfaces a consumer implements — adding a method to one is a breaking change;
- transitive dependency versions a consumer shares with you (see `dependencies`).

## Questions

- Is versioning declared and honored? If semver is claimed, does the history match it — find a minor release that
  broke something, and name it.
- What enforces compatibility mechanically: `japicmp`, `revapi`, `api-diff`, `cargo-semver-checks`, a golden-file test
  of the wire format, a schema registry? If nothing does, that is the top finding of this axis.
- What is public by accident? Types in an exported package that were meant to be internal, fields that should be
  private, a constructor that pins a construction path. Compare the intended surface (docs, `module-info`, `__all__`,
  `pub(crate)`) against the actual one.
- Is there a deprecation policy, and is it followed? A deprecation with no replacement named, no removal version, and
  no migration note is decoration.
- Skew: which combinations of this component and its peers are supported simultaneously, and does anything test them?
  Rolling upgrades and mixed-version clusters live here.
- Forward compatibility of data: does the reader tolerate fields it does not know? Does the writer emit anything an
  older reader will reject?

## Method

1. Establish the baseline: the last released version, from the changelog or the registry. Diff the public surface
   against it (`sb surface`, `japicmp`, `cargo-semver-checks`, or a diff of generated API dumps).
2. For each break, decide whether it is source-only, binary, or behavioral. Behavioral breaks are the ones tooling
   misses and the ones that hurt most — an unchanged signature whose semantics moved.
3. For persisted and wire formats, take a payload written by the old version and read it with the new one. If you can
   do that in a test, do it.
4. Report the mechanism gap separately from the individual breaks, and rate it higher.
