# Axis: compatibility

What did this code promise people who already depend on it, and does the change keep it? First decide what the
repository is, from its build and README: a library or tool that others call or build against, or a service or
deployment that others run. Check the matching list, and both where it is both.

## Released contracts

A contract is what a release shipped. Take the newest release by version: the release tags sorted with `git tag --list
--sort=-v:refname`, skipping pre-release and moving tags such as `latest`, or the newest published package or chart
version. Where that release is not an ancestor of `<base>` (`git merge-base --is-ancestor`), compare with its tree
rather than with the base branch. An API, parameter, default, or format added after that release, on the base branch or
earlier in this change, is not a contract yet, and changing or removing it is not a finding. Where the repository has
no releases, treat the base branch as released.

## Support window

A Netcracker repository, on GitHub under `Netcracker/` or on the company's own GitLab, follows the platform policy
below, and a window the repository documents applies there only where it is longer. Any other repository follows the
window it documents in `AGENTS.md`, `CONTRIBUTING.md`, or a compatibility policy.

- A released contract stays until it is deprecated, and a deprecated one stays for 3 years after the deprecation date.
  The contract covers APIs, events, data formats, feature behavior, and deployment and runtime parameters with their
  names, meaning, defaults, and optionality. An optional parameter or feature that leaves existing consumers unchanged
  can be added at any time.
- Before the window ends, each of these is a break: removing or incompatibly changing the contract, renaming or removing
  a parameter, making an optional parameter required, changing a default so that existing consumers behave differently,
  and an upgrade that needs the consumer to edit its configuration, pipelines, or descriptors.
- A removal after the window ships in a new major version. Take the deprecation date from the repository: a deprecation
  annotation, the changelog, or the documentation. Where the repository does not record it, write a `kind: question`
  finding that asks for it. Where the change sets the version (a build file, a chart, a `!` or `BREAKING CHANGE` commit
  marker), check that it is a new major version; where the version is set at release time, ask in a `kind: question`
  finding.
- A change that deprecates something states, in a deprecation annotation, the changelog, or the description, what
  replaces it, the deprecation date, and the earliest removal date, at least 3 years later. The description names the
  entry in the platform deprecation registry.

## Library or tool

- Source and binary API.
- Behavior callers rely on: a result, an error, or a diagnostic that changes for an input that worked before, including
  a new error on code that compiled or ran cleanly, unless the user enabled a stricter mode that produces it. Name the
  input and the old and new outcome.
- Configuration: a renamed or removed option, a changed default or meaning.
- Output other tools parse: message text that is documented or matched by known consumers, a file format.
- Stored data the library or tool writes, migrates, compacts, expires, or deletes: apply the **Stored-data steps** check
  below.

## Service or deployment

- **Baseline:** where no support window applies and the repository documents no intentional breaking migration, use
  project-defined installation and deployment parameters that were valid two years before the head commit.
- **Contracts:** keep existing APIs and CRDs, request and schema payloads, and installation or deployment parameter sets
  valid. New fields and parameters must be optional or have compatibility-preserving defaults.
- **Dependencies:** do not make new external services or runtime integrations mandatory. Keep them disabled by default
  and require explicit opt-in.
- **Inherited state:** where the change reads or replaces something an earlier version left behind, ask which
  pre-existing state it will meet: configuration files, keys or certificates, persisted data or schemas, caches, lock
  files, and objects an earlier chart or `kubectl apply` created. Check that a test or a run starts from that state, not
  only from a fresh install, or that the change documents the remedy and shows it run on that state.
- **Stored-data steps:** where the change writes, migrates, compacts, expires, or deletes stored data in more than one
  step, or outside one transaction, list each step whose effect outlives the process. For each, say what the next start
  finds when the process stops between two steps, and check that the retry neither loses, duplicates, nor orphans data,
  and does not repeat an irreversible step. Check that a concurrent reader sees the old or the new state, never a mix;
  that a migration started on partially or fully migrated data finishes or leaves it unchanged; and that an item exactly
  at the retention or expiration age is kept or removed as the setting's name or documentation says.
- **Passed values:** where an existing setting (a pass-through variable, a flag, an environment variable) now reaches a
  consumer it did not reach before, list the names the new consumer reads that the old consumers also read, such as a
  values key both charts define. For each, say what a value meant for the old consumers does to the new one; the
  documented example does not settle it.
- Where the change touches stored data, configuration, an interface between components, or a deployment, also cover
  mixed-version operation, rolling upgrade, downgrade, rollback, migration ordering, deprecation, and fresh install.

## Not a finding

An intended break the description states, with the migration path a user follows. Under the platform policy, that
holds only for a removal after the window in a new major version, or for a break the description says was approved as
an exception to the policy. Where exact compatibility with a replaced technology is impractical, the finding is a
missing migration path, not the replacement.

## Severity

An unannounced break for an input, call, or configuration that worked before is `major`. A passed value that means
something else for the new consumer, or makes it ask for something nothing provides, is `major`. A stop between
steps, or a retry, that loses or duplicates stored data, or repeats an irreversible step, is `major`.
Under the platform policy, a break before the window ends, or a removal outside a new major version, is `major`. A
deprecation that does not state its replacement, deprecation date, earliest removal date, or registry entry is `minor`.
