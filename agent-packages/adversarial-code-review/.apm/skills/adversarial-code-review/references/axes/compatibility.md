# Axis: compatibility

What did this code promise people who already depend on it, and does the change keep it? First decide what the
repository is, from its build and README: a library or tool that others call or build against, or a service or
deployment that others run. Check the matching list, and both where it is both.

## Library or tool

- Source and binary API.
- Behavior callers rely on: a result, an error, or a diagnostic that changes for an input that worked before, including
  a new error on code that compiled or ran cleanly, unless the user enabled a stricter mode that produces it. Name the
  input and the old and new outcome.
- Configuration: a renamed or removed option, a changed default or meaning.
- Output other tools parse: message text that is documented or matched by known consumers, a file format.

## Service or deployment

- **Baseline:** unless the repository documents a different support window or intentional breaking migration, use
  project-defined installation and deployment parameters that were valid two years before the head commit.
- **Contracts:** keep existing APIs and CRDs, request and schema payloads, and installation or deployment parameter sets
  valid. New fields and parameters must be optional or have compatibility-preserving defaults.
- **Dependencies:** do not make new external services or runtime integrations mandatory. Keep them disabled by default
  and require explicit opt-in.
- **Inherited state:** where the change reads or replaces something an earlier version left behind, ask which
  pre-existing state it will meet: configuration files, keys or certificates, persisted data or schemas, caches, lock
  files, and objects an earlier chart or `kubectl apply` created. Check that a test or a run starts from that state, not
  only from a fresh install, or that the change documents the remedy and shows it run on that state.
- **Passed values:** where an existing setting (a pass-through variable, a flag, an environment variable) now reaches a
  consumer it did not reach before, list the names the new consumer reads that the old consumers also read, such as a
  values key both charts define. For each, say what a value meant for the old consumers does to the new one; the
  documented example does not settle it.
- Where the change touches stored data, configuration, an interface between components, or a deployment, also cover
  mixed-version operation, rolling upgrade, downgrade, rollback, migration ordering, deprecation, and fresh install.

## Not a finding

An intended break the description states, with the migration path a user follows. Where exact compatibility with a
replaced technology is impractical, the finding is a missing migration path, not the replacement.

## Severity

An unannounced break for an input, call, or configuration that worked before is `major`. A passed value that means
something else for the new consumer, or makes it ask for something nothing provides, is `major`.
