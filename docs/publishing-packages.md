# Publishing packages

This repository is an APM marketplace. The index is the `marketplace:` block in the root `apm.yml`, compiled to
`.claude-plugin/marketplace.json` by `apm pack`. Both files are committed.

There are two kinds of work, and they stay separate:

- **Authoring** — add or update a package. You do this through a pull request, and your steps end at merge. The rest
  of this guide, except the last section, is for authors.
- **Releasing the marketplace** — cut the tag `vX.Y.Z` that consumers pin. This is automated; see
  [Releasing the marketplace](#releasing-the-marketplace). Authors never run it.

A package reaches the marketplace in one of two ways:

- **In this repository** — the package lives under `agent-packages/<name>/` and is listed as a local-path entry. Use
  this for packages this team owns.
- **In another repository** — the package lives and is released elsewhere; the marketplace holds only a remote entry
  that points at it. Use this to curate packages other repositories own.

## Conventions in this repository

- `.claude-plugin/marketplace.json` is generated, never hand-edited. Regenerate it with `apm pack` and commit the result.
- Local-path packages live one per directory under `agent-packages/<name>/`, each with its own `apm.yml` and `.apm/`
  source tree.
- Remote entries either pin a tag/SHA (`ref:`) or track a semver range (`version:` + `tag_pattern:`) — never a branch;
  `apm pack` rejects a mutable branch ref.
- Every change lands through a pull request.

## Prerequisites

- APM 0.16.0 or newer (`apm --version`, `apm self-update`).
- `gh` authenticated, for opening pull requests.

## Add a package that lives in this repository

1. Create the package under `agent-packages/<name>/`. At minimum it needs an `apm.yml` (`name`, `version`,
   `description`) and an `.apm/` tree with your primitives. The layout is described in
   [the APM package anatomy](https://microsoft.github.io/apm/concepts/package-anatomy/).

   ```text
   agent-packages/<name>/
     apm.yml
     .apm/
       skills/<name>/SKILL.md
       instructions/<name>.instructions.md
   ```

1. Add a local-path entry to the root `apm.yml` `marketplace:` block:

   ```yaml
   marketplace:
     packages:
       - name: <name>
         description: <one-line summary that consumers see>
         source: ./agent-packages/<name>
         version: <semver, matching the package's own apm.yml>
         tags: ["<tag>", ...]   # free-form labels; see "Tagging packages for discovery"
   ```

   Local-path entries do not inherit `description` or `version`, so set them here. Tags are optional but aid
   discovery; see [Tagging packages for discovery](#tagging-packages-for-discovery).

1. Regenerate the index:

   ```bash
   apm pack   # writes .claude-plugin/marketplace.json
   ```

1. Open a pull request with three things: the new `agent-packages/<name>/` tree, the updated root `apm.yml`, and the
   regenerated `.claude-plugin/marketplace.json`.

Once merged, the package is on `main`. It reaches consumers who pin a tag at the next
[marketplace release](#releasing-the-marketplace).

## Add a package from another repository

The package is developed and released in its own repository (`owner/repo`). Here you add only a pointer; no package
files land in this repository. A branch ref is never allowed — `apm pack` rejects it as mutable. Pick how the entry
tracks upstream:

- **Pin a tag or SHA** (`ref:`) — frozen and exact. The entry changes only when you edit it by hand, and
  `apm marketplace outdated` skips it.
- **Track a semver range** (`version:` + `tag_pattern:`) — `apm pack` resolves the highest matching tag and records it
  concretely in `marketplace.json`; `apm marketplace outdated` reports newer tags, and re-running `apm pack` adopts the
  newest in range.

1. Add a remote entry to the root `apm.yml` `marketplace:` block, in one of the two forms.

   Pinned to a tag or SHA:

   ```yaml
   marketplace:
     packages:
       - name: <name>
         source: <owner>/<repo>
         # subdir: <path/in/repo>   # only when the package sits in a subdirectory
         ref: v<X.Y.Z>             # a tag or commit SHA in <owner>/<repo>
         tags: ["<tag>", ...]   # free-form labels; see "Tagging packages for discovery"
   ```

   Tracking a semver range:

   ```yaml
   marketplace:
     packages:
       - name: <name>
         source: <owner>/<repo>
         # subdir: <path/in/repo>
         version: "^X.Y.Z"          # highest matching tag, resolved at pack time
         tag_pattern: "v{version}"  # how owner/repo names its tags; placeholders are {version} and {name}
         tags: ["<tag>", ...]   # free-form labels; see "Tagging packages for discovery"
   ```

   In both forms `name` is required — it is what consumers install by (`<name>@<marketplace>`) — and `description`
   is read from the package's own `apm.yml`, so you do not repeat it. The pinned form also takes the resolved
   `version` from that `apm.yml`; the range form sets `version:` to the constraint and records the matched tag in
   `source.ref`. `tag_pattern` defaults to the marketplace's `build.tagPattern`; set it per entry when a repository
   tags differently (`{name}-v{version}`, `release-{version}`, …). A pattern that does not match the repository's
   tags resolves to nothing. (Local-path entries are the exception to inheritance: `apm pack` does not read their
   `apm.yml`, so set `description`/`version` there yourself.) Tags are never inherited; see
   [Tagging packages for discovery](#tagging-packages-for-discovery).

1. Regenerate the index. `apm pack` resolves the remote ref through `git ls-remote`, so it needs network and read
   access to `owner/repo`:

   ```bash
   apm pack
   ```

1. Open a pull request with the updated `apm.yml` and the regenerated `.claude-plugin/marketplace.json` — no package source.

## Update a package

**A package in this repository.** Bump `version:` in `agent-packages/<name>/apm.yml` and the matching `version:` in
the marketplace entry, regenerate, and open a pull request:

```bash
apm pack
```

**A package from another repository.** This depends on how the entry tracks upstream:

- **Pinned (`ref:`)** — `apm marketplace outdated` skips it, so bump the `ref:` to the new upstream tag by hand, then regenerate.
- **Range (`version:` + `tag_pattern:`)** — `apm marketplace outdated` reports newer tags; re-running `apm pack`
  adopts the newest in range.

```bash
apm marketplace outdated   # reports entries with newer upstream tags (range entries only)
apm pack                   # adopts the newest in-range tag; for pinned entries, edit ref: first
```

## Validate before you open a pull request

```bash
apm pack --check-versions --check-clean --dry-run
```

This checks two things without writing to disk: every package declares a version consistent with
`marketplace.versioning.strategy` (`--check-versions`), and the committed `.claude-plugin/marketplace.json` matches
what `apm.yml` would produce (`--check-clean`). The `--dry-run` flag is required: without it, `apm pack` rewrites
`marketplace.json` first, so the drift check always passes. The same run resolves every remote entry's ref, so a
missing tag, a typo, or a mutable branch fails the gate.

CI runs the same command on every pull request — see
[`.github/workflows/marketplace.yml`](../.github/workflows/marketplace.yml); run it locally with `make check`. Do not
use `apm marketplace check` as the gate here: it probes entries as git remotes and reports local-path entries as
unreachable.

## What to commit

- A package in this repository: `agent-packages/<name>/` (the source), `apm.yml` (the entry), and `.claude-plugin/marketplace.json`.
- A package from another repository: `apm.yml` (the entry) and `.claude-plugin/marketplace.json` — no package source.

Keep `.claude-plugin/marketplace.json` tracked: if `*.json` is gitignored, add `!.claude-plugin/marketplace.json`.

## Tagging packages for discovery

Add `tags` to a package entry to label it. Tags are a free-form list of strings (up to 50 tags, 100 characters each):

```yaml
marketplace:
  packages:
    - name: go-microservice-dev-kit
      source: ./agent-packages/go-microservice-dev-kit
      version: 1.0.0
      tags: ["topic:devops", "stack:go", "stack:kubernetes", "activity:code-review", "activity:coding"]
```

- `keywords` is also accepted and is **merged into** the output `tags` array — there is no separate `keywords` field
  in `marketplace.json`.
- Tags are **not** inherited from a package's `apm.yml` (a package manifest has no tags); set them on the marketplace entry.
- `apm search` matches `name` and `description` only — **not** tags. Tags are for a catalogue or UI built over
  `marketplace.json`, and for runtimes that read it. To make a term findable from `apm search`, put it in the
  `description` as well.
- The `category` field is separate and surfaces only in the Codex output, so it does not appear in
  `.claude-plugin/marketplace.json`. For a Claude-output marketplace, use tags for thematic labels too.

There is no fixed tag vocabulary; pick a convention and apply it consistently. A self-documenting `axis:value` scheme
reads well (the `:` is allowed in a tag). Suggested axes — starting points, not a closed list:

| Axis | Meaning | Examples |
| --- | --- | --- |
| `topic:` | what the package is about | `topic:devops`, `topic:testing`, `topic:documentation`, `topic:api`, `topic:integration`, `topic:observability` |
| `stack:` | concrete technologies | `stack:go`, `stack:typescript`, `stack:react`, `stack:kubernetes`, `stack:nifi`, `stack:markdown` |
| `lang:` | natural language the package handles | `lang:en`, `lang:fr`, `lang:ru` |
| `activity:` | when it is used | `activity:authoring`, `activity:code-review`, `activity:testing`, `activity:release`, `activity:migration`, `activity:onboarding` |
| `audience:` | who it is for | `audience:public` (meant for reuse by other teams), `audience:internal` (published for reference, not for direct reuse) |

`audience:` is a soft signal, not a barrier — an `audience:internal` package is still installable. To keep packages
out of a consumable surface entirely, publish them in a separate marketplace instead.

## Releasing the marketplace

A marketplace release is a git tag `vX.Y.Z`. Consumers pin it (`apm marketplace add … --ref vX.Y.Z`), so the tag —
not a merge to `main` — is what ships authored changes to pinned consumers.

Releasing is automated by [`.github/workflows/release.yml`](../.github/workflows/release.yml). Pushing a tag runs the
workflow, which validates the index with `apm pack --check-versions --check-clean --dry-run` and publishes a GitHub
Release carrying `marketplace.json` and its SHA-256 checksum. Package authors do not run any of this.

To cut a release, a maintainer pushes a tag from a green `main`:

```bash
git switch main && git pull
git tag v<X.Y.Z>
git push origin v<X.Y.Z>
```

The tag must point at a commit whose `.claude-plugin/marketplace.json` is in sync; the release workflow fails closed otherwise.

## Reference

- [Publish to a marketplace](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/) — the authoring
  surface and the registry schema.
- [Repo shapes](https://microsoft.github.io/apm/producer/repo-shapes/) — single-plugin, aggregator, and
  monorepo-hybrid layouts.
- [Releasing from any CI](https://microsoft.github.io/apm/producer/releasing-from-any-ci/) — the release recipe this
  repository's `release` workflow is built on.
