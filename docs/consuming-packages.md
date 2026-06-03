# Consuming packages

This repository, `Netcracker/qubership-ai-packages`, publishes an APM marketplace: a curated index of agent packages
(skills, instructions, agents, and umbrella packages) that you install with the `apm` CLI. Register the marketplace
once, then install packages by name.

## Prerequisites

- APM 0.16.0 or newer. Check with `apm --version`; upgrade with `apm self-update`. Install steps are in
  [the APM installation guide](https://microsoft.github.io/apm/getting-started/installation/).
- Network access to `github.com`. The marketplace index and every package are fetched over git.

<!-- group doccmd[verify]: start -->

## Register the marketplace

```bash
apm marketplace add Netcracker/qubership-ai-packages --ref v0.1.0
```

`--ref` pins the whole marketplace, and every package in it, to a release tag, so every machine and CI run resolves
the same bytes. Omit `--ref` to track `main` and always resolve the latest
(`apm marketplace add Netcracker/qubership-ai-packages`).

Confirm the registration:

```bash
apm marketplace list
```

## Find a package

```bash
apm marketplace browse qubership-ai-packages
apm search authoring@qubership-ai-packages
```

`apm list` does not list packages — it lists the `scripts:` in your own `apm.yml`. Use `browse` or `search` to
explore the marketplace, and `apm deps list` to see what you have installed.

## Install a package

```bash
apm install apm-authoring@qubership-ai-packages
```

The install deploys the package's primitives (skills, instructions, and the rest) into your agent harness folders
(`.github/`, `.claude/`, `.cursor/`, and so on), records the resolved commit and content hash in `apm.lock.yaml`, and
adds the dependency to `apm.yml`. Commit both `apm.yml` and `apm.lock.yaml` so the install reproduces on every machine.

Inspect what you installed:

```bash
apm deps list
apm deps tree
```

`apm deps list` shows per-package primitive counts; `apm deps tree` shows the full graph, including transitive
dependencies. Umbrella packages such as `go-microservice-dev-kit` pull in other packages, which the tree lists.

## Remove a package

```bash
apm uninstall apm-authoring@qubership-ai-packages
```

This removes the package from `apm.yml` and `apm.lock.yaml`, deletes every file it deployed, and prunes transitive
dependencies that nothing else needs.

<!-- group doccmd[verify]: end -->

Unregister the marketplace itself:

<!-- skip doccmd[all]: next -->

```bash
apm marketplace remove qubership-ai-packages
```

## Staying up to date

`apm marketplace update` only refreshes the cached index — it does not change installed packages. Updating is three
moves: point the marketplace at the newer release, see what changed, then upgrade.

**Point at the newer release.** If you track `main` (added without `--ref`), refresh the cache:

<!-- skip doccmd[all]: next -->

```bash
apm marketplace update qubership-ai-packages
```

If you pinned a tag, re-register at the new one — re-adding under the same name updates the pin:

<!-- skip doccmd[all]: next -->

```bash
apm marketplace add Netcracker/qubership-ai-packages --ref v0.2.0
```

**See what changed.** Read-only; lists each installed package's current and latest version:

<!-- skip doccmd[all]: next -->

```bash
apm outdated
```

**Upgrade everything outdated** and rewrite `apm.lock.yaml`:

<!-- skip doccmd[all]: next -->

```bash
apm install --update
```

You do not track changes by hand — `apm outdated` reports them and `apm install --update` applies them all.
`apm update` does the same upgrade step but previews the plan and asks before writing.

## If a package leaves the marketplace

A package you installed is recorded in your `apm.yml` and `apm.lock.yaml` as a git dependency, independent of the
marketplace index. If the marketplace later drops the package, your project is unaffected: it stays installed, and
`apm install --update` does not remove it. Remove it yourself when you no longer need it:

<!-- skip doccmd[all]: next -->

```bash
apm uninstall apm-authoring@qubership-ai-packages
```

## How CI verifies this guide

The commands from "Register the marketplace" through "Remove a package" run on every pull request via
[`.github/workflows/marketplace.yml`](../.github/workflows/marketplace.yml). CI extracts the code blocks in the
[doccmd](https://github.com/adamtheturtle/doccmd) `verify` group and runs them against the revision under review, so
this guide cannot silently drift from what the CLI does. Run the same check locally with `make verify-docs` (push your
branch first).

## Reference

- [Installing from marketplaces](https://microsoft.github.io/apm/consumer/installing-from-marketplaces/) — the full
  consumer surface and the native install paths for Claude Code, Copilot, and Cursor.
- [Manage dependencies](https://microsoft.github.io/apm/consumer/manage-dependencies/) — update, audit, and the
  lockfile workflow.
